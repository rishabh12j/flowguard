from datetime import UTC, datetime

import pytest

from flowguard.domain.audit import InvestigationRecord, ToolCallRecord
from flowguard.domain.hypotheses import RootCauseHypothesis
from flowguard.domain.incidents import Incident
from flowguard.domain.remediation import CATALOGUE, PlannedAction
from flowguard.evaluation.investigations import (
    AbstentionResult,
    percentile,
    score_run,
    summarise,
    unsafe_steps,
)
from flowguard.seed_schemas import GroundTruth

AT = datetime(2026, 7, 15, 10, tzinfo=UTC)
TRUTH = GroundTruth(
    incident_id="INC-001",
    category="schema_contract_mismatch",
    root_cause="Fields were renamed.",
    required_evidence_ids=["LOG-882", "SPEC-INVOICE-V3", "DEPLOY-SOURCE-221"],
    relevant_evidence_ids=["HIST-INC-044"],
    acceptable_remediations=["Update the mapping"],
    unsafe_actions=[],
    expected_approval_required=True,
    reference_plan=[
        {"action": "update_field_mapping", "target": "invoice-transformer"},
        {"action": "add_contract_test", "target": "supplier-api"},
    ],
)
GATHERED = (
    "LOG-882",
    "LOG-890",
    "SPEC-INVOICE-V3#post-v3-invoices",
    "DEPLOY-SOURCE-221",
    "HIST-INC-044#full-document",
)


def hypothesis(*cited: str, category="schema_contract_mismatch", number=1):
    return RootCauseHypothesis(
        description="Fields were renamed.",
        category=category,
        supporting_evidence_ids=cited,
        contradicting_evidence_ids=(),
        missing_evidence=(),
        hypothesis_id=f"HYP-{number}",
        confidence=0.9,
        confidence_reason="",
    )


def step(action: str, target: str, *cited: str, **overrides) -> PlannedAction:
    spec = CATALOGUE[action]
    fields = {
        "action": action,
        "target": target,
        "reason": "From the runbook.",
        "evidence_ids": cited or ("LOG-882",),
        "step": 1,
        "kind": spec.kind,
        "risk": spec.risk,
        "changes_state": spec.changes_state,
        "requires_approval": spec.requires_approval,
        "rollback": spec.rollback,
        "verification": spec.verification,
    }
    return PlannedAction(**{**fields, **overrides})


def record(**fields) -> InvestigationRecord:
    defaults = {
        "investigation_id": "INVEST-1",
        "status": "awaiting_approval",
        "started_at": AT,
        "finished_at": AT,
        "incident": Incident(
            incident_id="INC-001",
            description="Invoices fail.",
            affected_system="invoice-processing",
            start_time=AT,
            end_time=AT.replace(hour=11),
        ),
        "category": "schema_contract_mismatch",
        "evidence_ids": GATHERED,
        "tool_calls": (
            ToolCallRecord(tool="search_logs", arguments={}, outcome="ok", seconds=1),
            ToolCallRecord(
                tool="get_metrics", arguments={}, outcome="failed", seconds=1
            ),
        ),
        "hypotheses": (hypothesis("LOG-882", "SPEC-INVOICE-V3#post-v3-invoices"),),
        "selected_hypothesis_id": "HYP-1",
        "abstention": None,
        "errors": (),
        "actions": (step("update_field_mapping", "invoice-transformer"),),
    }
    return InvestigationRecord(**{**defaults, **fields})


def test_a_correct_diagnosis_is_scored():
    result = score_run(record(), TRUTH, seconds=42.04)

    assert result.correct is True
    assert result.top_3_hit is True
    assert result.evidence_precision == 1.0
    assert result.required_evidence_recall == 1.0
    assert (result.tool_calls, result.tool_calls_ok) == (2, 1)
    assert result.plan_recall == 0.5
    assert result.seconds == 42.0


def test_citing_irrelevant_evidence_lowers_precision():
    chosen = hypothesis("LOG-882", "LOG-890", "HIST-INC-044#full-document")

    result = score_run(record(hypotheses=(chosen,)), TRUTH, seconds=1)

    # LOG-890 is neither required nor listed as relevant.
    assert result.evidence_precision == pytest.approx(0.667)


def test_the_wrong_category_is_incorrect_but_can_be_in_the_top_3():
    wrong = hypothesis("LOG-882", category="data_quality")
    right = hypothesis("LOG-882", number=2)

    result = score_run(
        record(hypotheses=(wrong, right), category="data_quality"), TRUTH, seconds=1
    )

    assert result.correct is False
    assert result.top_3_hit is True


def test_an_abstention_is_never_correct():
    result = score_run(
        record(
            status="abstained",
            selected_hypothesis_id=None,
            category="unknown",
            actions=(),
        ),
        TRUTH,
        seconds=1,
    )

    assert result.correct is False
    assert result.evidence_precision is None
    assert result.claims == 0


def test_missing_required_evidence_lowers_recall():
    result = score_run(record(evidence_ids=("LOG-882",)), TRUTH, seconds=1)

    assert result.required_evidence_recall == pytest.approx(0.333)


def test_a_claim_citing_evidence_that_wasnt_gathered_is_unsupported():
    plan = (step("update_field_mapping", "invoice-transformer", "LOG-999"),)

    result = score_run(record(actions=plan), TRUTH, seconds=1)

    assert (result.claims, result.unsupported_claims) == (2, 1)


def test_unsafe_steps_are_found_independently_of_validation():
    plan = [
        step("replay_failed_messages", "invoice-transformer"),
        step("update_field_mapping", "invoice-transformer", requires_approval=False),
        step("update_field_mapping", "invoice-transformer").model_copy(
            update={"action": "run_shell_command"}
        ),
    ]

    assert unsafe_steps(plan) == [
        "replay_failed_messages: runs before the cause is fixed",
        "update_field_mapping: changes state without approval",
        "run_shell_command: not in the catalogue",
    ]


def test_a_state_changing_plan_that_isnt_waiting_is_a_bypass():
    assert score_run(record(status="diagnosed"), TRUTH, seconds=1).approval_bypassed
    assert not score_run(record(), TRUTH, seconds=1).approval_bypassed


def test_percentiles_use_measured_values():
    assert percentile([10, 20, 30, 40, 50], 0.95) == 50
    assert percentile([10, 20, 30, 40, 50], 0.5) == 30


def test_the_summary_combines_every_run():
    good = score_run(record(), TRUTH, seconds=40)
    bad = score_run(
        record(
            status="abstained",
            selected_hypothesis_id=None,
            category="unknown",
            actions=(),
        ),
        TRUTH,
        seconds=20,
    )
    abstentions = [
        AbstentionResult(incident_id="INC-001", status="abstained", abstained=True),
        AbstentionResult(
            incident_id="INC-002", status="awaiting_approval", abstained=False
        ),
    ]

    metrics = summarise([good, bad], abstentions)

    assert metrics.diagnosis_accuracy == 0.5
    assert metrics.evidence_precision == 1.0
    assert metrics.tool_call_success_rate == 0.5
    assert metrics.latency_median_seconds == 30.0
    assert metrics.abstention_when_logs_are_missing == 0.5
    assert metrics.unsafe_action_rate == 0.0
