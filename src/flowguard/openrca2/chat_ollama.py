"""The baseline agent's conversation on a local model, through Ollama's chat API.

Ollama's own endpoint is used rather than its OpenAI-compatible one because only
it takes the context length (`num_ctx`). A local model's context is the limit
that matters here: when the history outgrows it, Ollama drops the oldest part
without an error, so each turn records whether the prompt came near the limit.
"""

from typing import Any

import httpx

from flowguard.openrca2.chat import ModelFailed, ToolCall, ToolSpec, Turn, Usage

NEAR_FULL = 0.95
RETRIES = 5


def _error_text(response: httpx.Response) -> str:
    """Ollama's own error message, from the response body."""
    try:
        return str(response.json().get("error", response.text))[:500]
    except ValueError:
        return response.text[:500]


class OllamaConversation:
    def __init__(
        self,
        model: str,
        system: str,
        first: str,
        tools: list[ToolSpec],
        *,
        host: str = "http://localhost:11434",
        num_ctx: int = 131072,
        temperature: float = 0.7,
        timeout: float = 1800.0,
        answer_format: dict[str, Any] | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.model = model
        self.num_ctx = num_ctx
        self.temperature = temperature
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters,
                },
            }
            for t in tools
        ]
        self.messages: list[dict[str, Any]] = [
            {"role": "system", "content": system},
            {"role": "user", "content": first},
        ]
        # A JSON schema the answer turn must follow. Ollama has no tool_choice,
        # so without it a model can call a tool at the answer turn and give no answer.
        self.answer_format = answer_format
        self._http = httpx.Client(base_url=host, timeout=timeout, transport=transport)
        self._count = 0

    def _call(
        self, tools: bool, answer: bool = False, schema: dict[str, Any] | None = None
    ) -> Turn:
        body: dict[str, Any] = {
            "model": self.model,
            "messages": self.messages,
            "stream": False,
            "options": {"num_ctx": self.num_ctx, "temperature": self.temperature},
        }
        if tools:
            body["tools"] = self.tools
        if answer and (schema or self.answer_format) is not None:
            body["format"] = schema or self.answer_format
        # As the paper's harness, a failed request is retried, up to 5 times. Ollama
        # answers 500 when it cannot parse what the model wrote (a malformed tool
        # call); at a temperature above 0 a new sample usually parses.
        failures: list[str] = []
        while True:
            try:
                response = self._http.post("/api/chat", json=body)
            except httpx.HTTPError as error:
                raise ModelFailed(f"Ollama could not be reached: {error}") from error
            if response.status_code < 500 or len(failures) == RETRIES:
                break
            failures.append(_error_text(response))
        if response.status_code >= 400:
            raise ModelFailed(
                f"Ollama failed with {response.status_code}: {_error_text(response)}"
                + (
                    f" (after {len(failures)} retries: {'; '.join(failures)})"
                    if failures
                    else ""
                )
            )
        data = response.json()
        message = data.get("message", {})
        self.messages.append(
            {
                k: v
                for k, v in message.items()
                if k in ("role", "content", "thinking", "tool_calls")
            }
        )
        calls = []
        for raw in message.get("tool_calls") or []:
            fn = raw.get("function", {})
            self._count += 1
            args = fn.get("arguments") or {}
            calls.append(
                ToolCall(
                    raw.get("id") or f"call_{self._count}",
                    fn.get("name", ""),
                    args if isinstance(args, dict) else {"raw": args},
                )
            )
        usage = Usage(
            prompt=int(data.get("prompt_eval_count") or 0),
            output=int(data.get("eval_count") or 0),
        )
        notes = [f"Ollama failed and the request was retried: {f}" for f in failures]
        if usage.prompt >= NEAR_FULL * self.num_ctx:
            notes.append(
                f"prompt of {usage.prompt} tokens near the context of {self.num_ctx}; older history may be dropped"
            )
        return Turn(
            message.get("content") or "",
            calls,
            usage,
            str(data.get("done_reason")),
            notes,
        )

    def ask(self) -> Turn:
        return self._call(tools=True)

    def answer_tools(self, results: list[tuple[ToolCall, str]]) -> None:
        for call, result in results:
            self.messages.append(
                {"role": "tool", "content": result, "tool_name": call.name}
            )

    def conclude(
        self, system: str | None, prompt: str, schema: dict[str, Any] | None = None
    ) -> Turn:
        if system is not None:
            self.messages[0] = {"role": "system", "content": system}
        self.messages.append({"role": "user", "content": prompt})
        return self._call(tools=False, answer=True, schema=schema)

    def transcript(self) -> list[dict[str, Any]]:
        return list(self.messages)
