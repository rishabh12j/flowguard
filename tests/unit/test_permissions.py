import pytest
from pydantic import ValidationError

from flowguard.mcp.permissions import (
    POLICIES,
    ToolDenied,
    ToolGuard,
    ToolPolicy,
    read_policy,
)

ALLOWED = {"service"}


def guard_with_limit(limit: int) -> ToolGuard:
    return ToolGuard({"search_logs": read_policy("search_logs", max_calls=limit)})


def test_allows_a_tool_with_a_policy():
    policy = guard_with_limit(1).authorise("search_logs", {"service": "x"}, ALLOWED)

    assert policy.name == "search_logs"


def test_denies_a_tool_without_a_policy():
    with pytest.raises(ToolDenied, match="not an allowed tool"):
        ToolGuard().authorise("delete_everything", {}, set())


def test_denies_an_unknown_argument():
    with pytest.raises(ToolDenied, match="shell"):
        guard_with_limit(1).authorise("search_logs", {"shell": "rm -rf"}, ALLOWED)


def test_allows_calls_up_to_the_limit_then_denies():
    guard = guard_with_limit(2)
    guard.authorise("search_logs", {}, ALLOWED)
    guard.authorise("search_logs", {}, ALLOWED)

    with pytest.raises(ToolDenied, match="call limit"):
        guard.authorise("search_logs", {}, ALLOWED)


def test_rejected_arguments_use_up_the_limit():
    guard = guard_with_limit(1)
    with pytest.raises(ToolDenied, match="shell"):
        guard.authorise("search_logs", {"shell": "rm -rf"}, ALLOWED)

    with pytest.raises(ToolDenied, match="call limit"):
        guard.authorise("search_logs", {}, ALLOWED)


def test_limits_are_counted_per_tool():
    guard = ToolGuard(
        {
            "search_logs": read_policy("search_logs", max_calls=1),
            "get_api_spec": read_policy("get_api_spec", max_calls=1),
        }
    )
    guard.authorise("search_logs", {}, ALLOWED)

    guard.authorise("get_api_spec", {}, ALLOWED)


def test_each_investigation_gets_its_own_limit():
    policies = {"search_logs": read_policy("search_logs", max_calls=1)}
    ToolGuard(policies).authorise("search_logs", {}, ALLOWED)

    ToolGuard(policies).authorise("search_logs", {}, ALLOWED)


def test_denies_a_tool_that_requires_approval():
    policy = ToolPolicy(
        name="replay_messages",
        permission="write",
        risk="high",
        requires_approval=True,
        max_calls_per_investigation=1,
        timeout_seconds=10,
    )

    with pytest.raises(ToolDenied, match="requires approval"):
        ToolGuard({"replay_messages": policy}).authorise("replay_messages", {}, set())


def test_a_write_policy_must_require_approval():
    with pytest.raises(ValidationError, match="must require approval"):
        ToolPolicy(
            name="replay_messages",
            permission="write",
            risk="high",
            requires_approval=False,
            max_calls_per_investigation=1,
            timeout_seconds=10,
        )


def test_a_policy_needs_a_limit_of_at_least_one():
    with pytest.raises(ValidationError):
        read_policy("search_logs", max_calls=0)


def test_every_mvp_tool_is_read_only():
    assert all(policy.permission == "read" for policy in POLICIES.values())
    assert not any(policy.requires_approval for policy in POLICIES.values())
