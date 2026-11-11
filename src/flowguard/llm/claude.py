"""Claude through the Anthropic API, for comparing models in an evaluation.

FlowGuard runs on a local model. This client exists to measure how much a
stronger model changes the results. It needs the optional `claude` extra and
an API key in ANTHROPIC_API_KEY, which must never be written into the repo.
"""

import copy
from typing import Any, Literal

import anthropic
from anthropic.types import MessageParam, OutputConfigParam, ThinkingConfigParam

from flowguard.llm.client import LLMError, ModelDeclined

CLAUDE_MODEL = "claude-sonnet-5-5"

Effort = Literal["low", "medium", "high"]

# Claude's structured outputs reject these keywords. FlowGuard's parsers check
# them after every answer, so dropping them from the schema loses no check.
UNSUPPORTED = {
    "minLength",
    "maxLength",
    "maxItems",
    "minimum",
    "maximum",
    "exclusiveMinimum",
    "exclusiveMaximum",
    "multipleOf",
    "pattern",
}


def claude_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """The schema without the constraints Claude's structured outputs reject."""

    def strip(node: Any) -> Any:
        if isinstance(node, dict):
            kept = {}
            for key, value in node.items():
                if key in ("properties", "$defs") and isinstance(value, dict):
                    # Field names, not keywords: the explain path's reading has a
                    # field called "pattern", which must stay.
                    kept[key] = {name: strip(field) for name, field in value.items()}
                elif key not in UNSUPPORTED and not (
                    # Only "at least one" is supported; "at least two" is asked for
                    # in the prompt and checked by code instead.
                    key == "minItems" and value > 1
                ):
                    kept[key] = strip(value)
            return kept
        if isinstance(node, list):
            return [strip(item) for item in node]
        return node

    return strip(copy.deepcopy(schema))  # type: ignore[no-any-return]


class ClaudeLLM:
    def __init__(
        self,
        model: str = CLAUDE_MODEL,
        *,
        client: anthropic.Anthropic | None = None,
        effort: Effort | None = None,
        max_tokens: int = 16000,
    ) -> None:
        self.model = model
        self.effort = effort
        self.max_tokens = max_tokens
        # The SDK retries rate limits, overloads, and server errors itself.
        self._client = client or anthropic.Anthropic(max_retries=4, timeout=300.0)
        # Totals across every call, so a run's cost can be worked out.
        self.input_tokens = 0
        self.output_tokens = 0

    def generate(self, system: str, prompt: str, schema: dict[str, Any]) -> str:
        output_config: OutputConfigParam = {
            "format": {"type": "json_schema", "schema": claude_schema(schema)}
        }
        messages: list[MessageParam] = [{"role": "user", "content": prompt}]
        thinking: ThinkingConfigParam
        if self.effort is None:
            # Sonnet 5.5 can't disable thinking; between_tools is how it's
            # turned off, which matches how Gemma runs.
            thinking = {"type": "between_tools"}
        else:
            thinking = {"type": "adaptive"}
            output_config["effort"] = self.effort
        try:
            response = self._client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system,
                messages=messages,
                output_config=output_config,
                thinking=thinking,
            )
        except anthropic.APITimeoutError as error:
            raise LLMError(f"{self.model} did not answer in time") from error
        except anthropic.APIStatusError as error:
            raise LLMError(
                f"{self.model} failed with {error.status_code}: {error.message[:200]}"
            ) from error
        except anthropic.APIConnectionError as error:
            raise LLMError(f"could not reach the Anthropic API: {error}") from error

        self.input_tokens += response.usage.input_tokens
        self.output_tokens += response.usage.output_tokens
        if response.stop_reason == "refusal":
            details = response.stop_details
            category = details.category if details else None
            raise ModelDeclined(f"{self.model} declined to answer ({category})")
        # A cut-off answer is returned as it is; the parser rejects it as the
        # model's answer, as it would any other broken one.
        return "".join(block.text for block in response.content if block.type == "text")
