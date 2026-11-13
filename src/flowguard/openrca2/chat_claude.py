"""The baseline agent's conversation on a Claude model, through the Anthropic SDK.

The whole history is resent each turn, with automatic prompt caching so the part
already sent is billed at the cache-read price. No temperature is sent: the
current Haiku and Sonnet models refuse any value but the default, so the paper's
0.7 cannot be used on them.

Thinking blocks. On current models a thinking block is bound to everything sent
before it (system prompt, tools, earlier messages), and replaying it after any of
that changed is a 400 on accounts created since 2026-08-31. So:

- Each response is kept exactly as it came over the wire and sent back as such,
  never rebuilt from the SDK's objects.
- The answer turn, which the paper runs as a separate call with its own system
  prompt, is sent with every thinking block removed: none is replayed, so none is
  checked. The investigation turns are untouched.
- With `binding` set, requests carry the thinking-binding controls (beta
  `thinking-binding-controls-2026-08-01`): "error" fails loudly on any edit,
  "drop_block" drops a failing block and goes on. Either way each response's
  `input_transformations` is recorded in the turn's notes.
- With `capture` set, each request body is appended to that file, one per line,
  for the reference's `prefix_diff.py` and `drop_block_probe.py`.
"""

import json
from pathlib import Path
from typing import Any

import anthropic

from flowguard.llm.claude import claude_schema
from flowguard.openrca2.chat import ModelFailed, ToolCall, ToolSpec, Turn, Usage

# USD per million tokens, from the Claude API reference cached 2026-11-03.
# (input, output, cache read). Cache writes cost 1.25 times input (5-minute TTL).
PRICES = {
    "claude-haiku-5-5": (0.10, 0.50, 0.01),
    "claude-sonnet-5-5": (2.00, 10.00, 0.10),
    "claude-sonnet-5": (2.00, 10.00, 0.20),
    "claude-opus-5-5": (4.00, 20.00, 0.20),
}
# Haiku 5.5's prices for a prompt above 100K tokens. Its cache-read price at
# that size is not stated; a tenth of input is assumed.
HAIKU_LONG = (0.50, 2.50, 0.05)
WRITE = 1.25
BINDING_BETA = "thinking-binding-controls-2026-08-01"
THINKING_TYPES = ("thinking", "redacted_thinking")


def cost(model: str, usage: Usage) -> float:
    if model not in PRICES:
        return 0.0
    price_in, price_out, price_read = PRICES[model]
    if model == "claude-haiku-5-5" and usage.prompt > 100_000:
        price_in, price_out, price_read = HAIKU_LONG
    uncached = usage.prompt - usage.cache_write - usage.cache_read
    return (
        uncached * price_in
        + usage.cache_write * price_in * WRITE
        + usage.cache_read * price_read
        + usage.output * price_out
    ) / 1e6


def without_thinking(messages: list[Any]) -> list[Any]:
    """The history with every thinking block removed, for a call that replays none."""
    out = []
    for m in messages:
        content = m["content"]
        if m["role"] == "assistant" and isinstance(content, list):
            content = [b for b in content if b.get("type") not in THINKING_TYPES]
            if not content:
                continue
        out.append({**m, "content": content})
    return out


class ClaudeConversation:
    def __init__(
        self,
        model: str,
        system: str,
        first: str,
        tools: list[ToolSpec],
        *,
        client: anthropic.Anthropic | None = None,
        max_tokens: int = 16000,
        binding: str | None = None,
        capture: Path | None = None,
    ) -> None:
        if binding not in (None, "error", "drop_block"):
            raise ValueError(f"binding must be error or drop_block, not {binding!r}")
        self.model = model
        self.system = system
        self.tools: list[Any] = [
            {"name": t.name, "description": t.description, "input_schema": t.parameters}
            for t in tools
        ]
        self.messages: list[Any] = [{"role": "user", "content": first}]
        self.max_tokens = max_tokens
        self.binding = binding
        self.capture = capture
        self.spent = 0.0
        # The SDK retries rate limits, overloads and server errors itself.
        self._client = client or anthropic.Anthropic(max_retries=4, timeout=600.0)

    def _call(
        self,
        system: str,
        tool_choice: dict[str, str],
        messages: list[Any],
        schema: dict[str, Any] | None = None,
    ) -> Turn:
        body: dict[str, Any] = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "system": system,
            "tools": self.tools,
            "tool_choice": tool_choice,
            "messages": messages,
            "cache_control": {"type": "ephemeral"},
        }
        if schema is not None:
            body["output_config"] = {
                "format": {"type": "json_schema", "schema": claude_schema(schema)}
            }
        if self.binding:
            body["thinking"] = {
                "type": "adaptive",
                "block_binding": {"prefix_mismatch_behavior": self.binding},
            }
        if self.capture:
            line = {
                "request": body,
                "headers": {"anthropic-beta": BINDING_BETA} if self.binding else {},
            }
            with self.capture.open("a", encoding="utf-8", newline="\n") as handle:
                handle.write(json.dumps(line, ensure_ascii=False) + "\n")
        try:
            if self.binding:
                raw = self._client.beta.messages.with_raw_response.create(
                    **body, betas=[BINDING_BETA]
                )
            else:
                raw = self._client.messages.with_raw_response.create(**body)
        except anthropic.APIStatusError as error:
            diagnosis = error.response.headers.get("anthropic-thinking-prefix-mismatch")
            raise ModelFailed(
                f"{self.model} failed with {error.status_code}: {error.message}"
                + (
                    f" [anthropic-thinking-prefix-mismatch: {diagnosis}]"
                    if diagnosis
                    else ""
                )
            ) from error
        except anthropic.APIConnectionError as error:
            raise ModelFailed(f"could not reach the Anthropic API: {error}") from error
        data = raw.http_response.json()  # the response exactly as sent
        u = data.get("usage") or {}
        write = u.get("cache_creation_input_tokens") or 0
        read = u.get("cache_read_input_tokens") or 0
        usage = Usage(
            prompt=(u.get("input_tokens") or 0) + write + read,
            cache_write=write,
            cache_read=read,
            output=u.get("output_tokens") or 0,
        )
        usage.usd = cost(self.model, usage)
        self.spent += usage.usd
        stop = str(data.get("stop_reason"))
        if stop == "refusal":
            details = data.get("stop_details") or {}
            raise ModelFailed(f"{self.model} declined ({details.get('category')})")
        notes = [
            f"input_transformation {t.get('type')}: {t.get('reason')} at {t.get('path')}"
            for t in data.get("input_transformations") or []
        ]
        content = data.get("content") or []
        self.messages.append({"role": "assistant", "content": content})
        calls = []
        if stop == "max_tokens":
            notes.append("the answer was cut off at max_tokens")
        else:
            calls = [
                ToolCall(b["id"], b["name"], dict(b.get("input") or {}))
                for b in content
                if b.get("type") == "tool_use"
            ]
        text = "".join(b.get("text", "") for b in content if b.get("type") == "text")
        return Turn(text, calls, usage, stop, notes)

    def ask(self) -> Turn:
        return self._call(self.system, {"type": "auto"}, self.messages)

    def answer_tools(self, results: list[tuple[ToolCall, str]]) -> None:
        # All results of one turn go back in one message.
        self.messages.append(
            {
                "role": "user",
                "content": [
                    {"type": "tool_result", "tool_use_id": c.id, "content": r}
                    for c, r in results
                ],
            }
        )

    def conclude(
        self, system: str | None, prompt: str, schema: dict[str, Any] | None = None
    ) -> Turn:
        self.messages.append({"role": "user", "content": prompt})
        if system is None:
            # Same system prompt and tools: nothing before the thinking blocks changed.
            return self._call(self.system, {"type": "none"}, self.messages, schema)
        return self._call(
            system, {"type": "none"}, without_thinking(self.messages), schema
        )

    def transcript(self) -> list[dict[str, Any]]:
        return [dict(m) for m in self.messages]
