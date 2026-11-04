from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from flowguard.domain.evidence import EvidenceItem
from flowguard.domain.hypotheses import RootCauseHypothesis
from flowguard.domain.remediation import CATALOGUE, ActionSpec, ProposedAction
from flowguard.domain.validation import check_actions, targets_in


def item(evidence_id: str, source_type: str, source_name: str) -> EvidenceItem:
    return EvidenceItem(
        evidence_id=evidence_id,
        source_type=source_type,
        source_name=source_name,
        title=evidence_id,
        content="",
        timestamp=datetime(2026, 7, 15, 9, 43, tzinfo=UTC),
        metadata={},
    )


EVIDENCE = (
    item("LOG-882", "log", "invoice-transformer"),
    item("DEPLOY-SOURCE-221", "deployment", "supplier-api"),
    item("SPEC-INVOICE-V3#post-v3-invoices", "api_spec", "invoice-transformer"),
    item("LOG-700", "log", "erp-connector"),
    item("RB-SCHEMA-COMPAT#full-document", "runbook", "invoice-transformer"),
    item("HIST-INC-044#full-document", "historical_incident", "invoice-transformer"),
)
ROOT_CAUSE = RootCauseHypothesis(
    description="supplier-api now sends camelCase fields.",
    category="schema_contract_mismatch",
    supporting_evidence_ids=("LOG-882", "DEPLOY-SOURCE-221"),
    contradicting_evidence_ids=(),
    missing_evidence=(),
    hypothesis_id="HYP-1",
    confidence=0.9,
    confidence_reason="",
)


def action(name: str, target: str = "invoice-transformer", *evidence_ids: str):
    return ProposedAction(
        action=name,
        target=target,
        reason="Fixes the mapping.",
        evidence_ids=evidence_ids or ("LOG-882",),
    )


def check(*proposed: ProposedAction):
    return check_actions(proposed, EVIDENCE, ROOT_CAUSE)


def problems(*proposed: ProposedAction) -> list[str]:
    return [rejected.problem for rejected in check(*proposed)[1]]


def test_targets_are_services_that_logged_or_deployed_and_deployments():
    assert targets_in(EVIDENCE) == {
        "service": {"invoice-transformer", "supplier-api", "erp-connector"},
        "deployment": {"DEPLOY-SOURCE-221"},
    }


def test_a_sound_plan_is_numbered_in_order():
    planned, rejected = check(
        action("update_field_mapping"),
        action("replay_failed_messages"),
        action("add_contract_test", "supplier-api"),
    )

    assert rejected == ()
    assert [(step.step, step.action) for step in planned] == [
        (1, "update_field_mapping"),
        (2, "replay_failed_messages"),
        (3, "add_contract_test"),
    ]


def test_risk_and_safeguards_come_from_the_catalogue():
    [planned], _ = check(action("update_field_mapping"))

    spec = CATALOGUE["update_field_mapping"]
    assert (planned.risk, planned.changes_state, planned.requires_approval) == (
        spec.risk,
        True,
        True,
    )
    assert (planned.rollback, planned.verification) == (
        spec.rollback,
        spec.verification,
    )


@pytest.mark.parametrize(
    "name", ["run_shell_command", "disable_payload_validation", "DROP TABLE invoices"]
)
def test_actions_outside_the_catalogue_are_rejected(name):
    assert problems(action(name)) == ["not an allowed action"]


def test_unknown_evidence_is_rejected():
    assert problems(
        action("update_field_mapping", "invoice-transformer", "LOG-999")
    ) == ["cites unknown evidence: ['LOG-999']"]


def test_an_action_justified_only_by_unrelated_evidence_is_rejected():
    proposed = action("update_field_mapping", "invoice-transformer", "LOG-700")

    assert problems(proposed) == [
        "cites neither the root cause's evidence nor a runbook or past incident"
    ]


@pytest.mark.parametrize(
    "guidance", ["RB-SCHEMA-COMPAT#full-document", "HIST-INC-044#full-document"]
)
def test_a_runbook_or_past_incident_can_justify_an_action(guidance):
    planned, rejected = check(action("add_contract_test", "supplier-api", guidance))

    assert rejected == ()
    assert planned[0].evidence_ids == (guidance,)


def test_a_service_target_must_appear_in_the_evidence():
    assert problems(action("update_field_mapping", "payments-db")) == [
        "its target is not a service in the evidence"
    ]


def test_a_rollback_must_target_a_deployment():
    assert problems(action("rollback_deployment", "supplier-api")) == [
        "its target is not a deployment in the evidence"
    ]
    planned, _ = check(action("rollback_deployment", "DEPLOY-SOURCE-221"))
    assert planned[0].risk == "high"


def test_a_replay_before_the_fix_is_rejected():
    planned, rejected = check(
        action("replay_failed_messages"), action("update_field_mapping")
    )

    assert [step.action for step in planned] == ["update_field_mapping"]
    assert rejected[0].problem == "must come after a step that fixes the cause"


def test_a_rejected_fix_does_not_allow_a_replay():
    _, rejected = check(
        action("update_field_mapping", "payments-db"), action("replay_failed_messages")
    )

    assert [item.proposed.action for item in rejected] == [
        "update_field_mapping",
        "replay_failed_messages",
    ]


def test_steps_are_numbered_after_rejections():
    planned, _ = check(action("run_shell_command"), action("add_contract_test"))

    assert planned[0].step == 1


def test_the_model_cannot_set_an_action_s_risk():
    with pytest.raises(ValidationError):
        ProposedAction(
            action="update_field_mapping",
            target="invoice-transformer",
            reason="",
            evidence_ids=("LOG-882",),
            risk="low",
        )


def test_every_state_change_needs_a_rollback():
    with pytest.raises(ValidationError, match="needs a rollback step"):
        ActionSpec(
            name="restart_service",
            purpose="restart a service",
            kind="mitigation",
            target="service",
            changes_state=True,
            risk="medium",
            verification="Confirm it is running.",
        )


def test_every_state_change_in_the_catalogue_needs_approval():
    for spec in CATALOGUE.values():
        assert spec.requires_approval is spec.changes_state
