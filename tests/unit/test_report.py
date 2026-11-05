from datetime import UTC, datetime

from flowguard.domain.approval import ApprovalDecision
from flowguard.domain.audit import InvestigationRecord, ToolCallRecord
from flowguard.domain.hypotheses import RootCauseHypothesis
from flowguard.domain.incidents import Incident
from flowguard.domain.remediation import (
    CATALOGUE,
    PlannedAction,
    ProposedAction,
    RejectedAction,
)
from flowguard.report import render_report

AT = datetime(2026, 7, 15, 10, 5, tzinfo=UTC)
INCIDENT = Incident(
    incident_id="INC-001",
    description="Invoice INV-2048 did not enter the approval workflow.",
    affected_system="invoice-processing",
    start_time=datetime(2026, 7, 15, 9, tzinfo=UTC),
    end_time=datetime(2026, 7, 15, 11, tzinfo=UTC),
)
CAUSE = RootCauseHypothesis(
    description="supplier-api renamed its fields to camelCase.",
    category="schema_contract_mismatch",
    supporting_evidence_ids=("LOG-882", "DEPLOY-SOURCE-221"),
    contradicting_evidence_ids=(),
    missing_evidence=(),
    hypothesis_id="HYP-1",
    confidence=0.9,
    confidence_reason="+0.30 cites an error log; +0.20 a cited change came first",
)
SPEC = CATALOGUE["update_field_mapping"]
STEP = PlannedAction(
    action="update_field_mapping",
    target="invoice-transformer",
    reason="Map supplierId to supplier_id.",
    evidence_ids=("LOG-882",),
    step=1,
    kind=SPEC.kind,
    risk=SPEC.risk,
    changes_state=True,
    requires_approval=True,
    rollback=SPEC.rollback,
    verification=SPEC.verification,
)


def record(**fields) -> InvestigationRecord:
    defaults = {
        "investigation_id": "INVEST-1",
        "status": "awaiting_approval",
        "started_at": AT,
        "finished_at": AT,
        "incident": INCIDENT,
        "category": "schema_contract_mismatch",
        "evidence_ids": ("LOG-882", "DEPLOY-SOURCE-221"),
        "tool_calls": (
            ToolCallRecord(tool="search_logs", arguments={}, outcome="ok", seconds=1),
            ToolCallRecord(
                tool="get_metrics", arguments={}, outcome="failed", seconds=1
            ),
        ),
        "hypotheses": (CAUSE,),
        "selected_hypothesis_id": "HYP-1",
        "abstention": None,
        "errors": (),
        "actions": (STEP,),
        "requires_approval": True,
    }
    return InvestigationRecord(**{**defaults, **fields})


def test_a_plan_waiting_for_approval_shows_cause_steps_and_safeguards():
    report = render_report(record())

    assert report.startswith("# INC-001: schema_contract_mismatch")
    assert "Waiting for a person to approve the plan." in report
    assert "confidence 0.90" in report
    assert "+0.30 cites an error log" in report
    assert (
        "1. **update_field_mapping** on `invoice-transformer`: medium risk, needs approval."
        in report
    )
    assert f"Roll back: {SPEC.rollback}" in report
    assert "2 tool calls (1 failed, 1 ok)" in report


def test_refused_steps_and_the_decision_are_reported():
    refused = RejectedAction(
        proposed=ProposedAction(
            action="run_shell_command",
            target="invoice-transformer",
            reason="Fix it fast.",
            evidence_ids=("LOG-882",),
        ),
        problem="not an allowed action",
    )
    decision = ApprovalDecision(
        decision="approve", approver="sam", comment="Looks right.", decided_at=AT
    )

    report = render_report(
        record(status="approved", rejected_actions=(refused,), decision=decision)
    )

    assert (
        "- run_shell_command on `invoice-transformer`: not an allowed action" in report
    )
    assert "approve by sam at 2026-07-15 10:05 UTC. Comment: Looks right." in report


def test_an_abstention_says_why():
    report = render_report(
        record(
            status="abstained",
            category="unknown",
            selected_hypothesis_id=None,
            abstention="the best hypothesis scored 0.30, below 0.65",
            actions=(),
        )
    )

    assert "No root cause was confident enough to report." in report
    assert "FlowGuard abstained: the best hypothesis scored 0.30, below 0.65." in report
    assert "## Plan" not in report


def test_a_rejected_request_has_no_incident_section():
    report = render_report(
        record(
            status="rejected",
            incident=None,
            category=None,
            hypotheses=(),
            selected_hypothesis_id=None,
            actions=(),
            errors=("affected_system: String should match pattern '^\\\\S+$'",),
        )
    )

    assert report.startswith("# Rejected request")
    assert "## Problems while investigating" in report
