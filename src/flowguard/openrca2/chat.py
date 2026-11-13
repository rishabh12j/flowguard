"""What the baseline agent needs from a model: a conversation that can call tools.

Each provider has its own file and keeps the conversation in its own format, so
that what the model wrote (thinking included) goes back to it unchanged.
"""

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    parameters: dict[str, Any]  # JSON schema of the arguments


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class Usage:
    """Tokens of one call. `prompt` is the whole prompt, however it was billed."""

    prompt: int = 0
    cache_write: int = 0
    cache_read: int = 0
    output: int = 0
    usd: float = 0.0


@dataclass
class Turn:
    text: str
    calls: list[ToolCall]
    usage: Usage
    stop: str  # the provider's reason for stopping
    notes: list[str] = field(default_factory=list)  # e.g. the context filled up


class ModelFailed(Exception):
    """The model could not answer: refused, unreachable, or broke the format."""


class Conversation(Protocol):
    def ask(self) -> Turn:
        """The model's next turn, with the tools available."""
        ...

    def answer_tools(self, results: list[tuple[ToolCall, str]]) -> None:
        """Give the model the results of the calls of its last turn."""
        ...

    def conclude(
        self, system: str | None, prompt: str, schema: dict[str, Any] | None = None
    ) -> Turn:
        """One last turn on the whole history, with no tool calls.

        `system` replaces the system prompt for this turn; None keeps it. `schema`
        holds the answer to a JSON schema.
        """
        ...

    def transcript(self) -> list[dict[str, Any]]:
        """The conversation as plain data, for the run's record."""
        ...
