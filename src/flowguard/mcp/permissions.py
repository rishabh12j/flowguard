from collections import Counter
from typing import Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ToolDenied(Exception):
    """A tool call was blocked before it reached a server."""


class ToolPolicy(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    permission: Literal["read", "write"]
    risk: Literal["low", "medium", "high"]
    requires_approval: bool
    max_calls_per_investigation: int = Field(ge=1)
    timeout_seconds: float = Field(gt=0)

    @model_validator(mode="after")
    def writes_need_approval(self) -> Self:
        if self.permission == "write" and not self.requires_approval:
            raise ValueError(f"{self.name} writes, so it must require approval")
        return self


def read_policy(name: str, max_calls: int) -> ToolPolicy:
    return ToolPolicy(
        name=name,
        permission="read",
        risk="low",
        requires_approval=False,
        max_calls_per_investigation=max_calls,
        timeout_seconds=10,
    )


POLICIES = {
    policy.name: policy
    for policy in (
        read_policy("search_logs", max_calls=10),
        read_policy("get_deployments", max_calls=5),
        read_policy("get_dependency_map", max_calls=5),
        read_policy("get_api_spec", max_calls=5),
    )
}


class ToolGuard:
    """Tracks one investigation's tool calls, so create one per investigation."""

    def __init__(self, policies: dict[str, ToolPolicy] = POLICIES) -> None:
        self._policies = policies
        self._calls: Counter[str] = Counter()

    def authorise(
        self, name: str, arguments: dict[str, Any], allowed_arguments: set[str]
    ) -> ToolPolicy:
        policy = self._policies.get(name)
        if policy is None:
            raise ToolDenied(f"{name} is not an allowed tool")
        if policy.requires_approval:
            raise ToolDenied(f"{name} requires approval")
        if self._calls[name] >= policy.max_calls_per_investigation:
            raise ToolDenied(f"{name} has reached its call limit")

        self._calls[name] += 1

        unknown = sorted(set(arguments) - allowed_arguments)
        if unknown:
            raise ToolDenied(f"{name} does not accept {unknown}")
        return policy
