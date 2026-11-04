from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from flowguard.domain.approval import ApprovalDecision

DECIDED_AT = datetime(2026, 7, 15, 12, tzinfo=UTC)


def decision(**fields) -> ApprovalDecision:
    return ApprovalDecision(
        **{"decision": "approve", "approver": "sam", "decided_at": DECIDED_AT, **fields}
    )


def test_an_approval_needs_no_comment():
    assert decision().comment == ""


@pytest.mark.parametrize("choice", ["reject", "request_more_evidence"])
def test_a_refusal_must_say_why(choice):
    with pytest.raises(ValidationError, match=f"{choice} needs a comment saying why"):
        decision(decision=choice)


def test_a_blank_comment_does_not_count():
    with pytest.raises(ValidationError, match="needs a comment"):
        decision(decision="reject", comment="   ")


def test_an_approver_is_required():
    with pytest.raises(ValidationError):
        decision(approver="  ")


def test_only_known_decisions_are_accepted():
    with pytest.raises(ValidationError):
        decision(decision="execute")


def test_the_time_must_have_a_timezone():
    with pytest.raises(ValidationError):
        decision(decided_at=datetime(2026, 7, 15, 12))
