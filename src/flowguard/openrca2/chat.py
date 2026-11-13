"""What the baseline agent needs from a model: a conversation that can call tools.

Each provider has its own file and keeps the conversation in its own format, so
that what the model wrote (thinking included) goes back to it unchanged.
"""

from collections import Counter
from collections.abc import Callable
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

    def add(self, other: "Usage") -> None:
        self.prompt += other.prompt
        self.cache_write += other.cache_write
        self.cache_read += other.cache_read
        self.output += other.output
        self.usd += other.usd


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


@dataclass
class Exploration:
    """What one agent did before it was asked for its answer."""

    calls: Counter[str]
    turns: int
    usage: Usage
    per_turn: list[tuple[int, int]]  # (prompt, output) tokens of each turn
    notes: list[str]
    stopped: str  # why it ended


def explore(
    conversation: Conversation,
    run_tool: Callable[[ToolCall], str],
    *,
    max_calls: int,
    refusal: str,
    budget: Callable[[float], bool] | None = None,
) -> Exploration:
    """Let the model call tools until it stops, reaches the cap or the money runs out.

    `refusal` is the result given to a call past the cap. `budget` is given what
    this exploration has spent and says whether to go on.
    """
    out = Exploration(Counter(), 0, Usage(), [], [], "the model stopped calling tools")
    while True:
        turn = conversation.ask()
        out.turns += 1
        out.usage.add(turn.usage)
        out.per_turn.append((turn.usage.prompt, turn.usage.output))
        out.notes += turn.notes
        if not turn.calls:
            break
        results = []
        for call in turn.calls:
            if sum(out.calls.values()) >= max_calls:
                results.append((call, refusal))
                continue
            out.calls[call.name] += 1
            results.append((call, run_tool(call)))
        conversation.answer_tools(results)
        if sum(out.calls.values()) >= max_calls:
            out.stopped = f"the cap of {max_calls} tool calls"
            break
        if budget is not None and not budget(out.usage.usd):
            out.stopped = "the spending limit"
            break
    return out
