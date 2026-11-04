import json
from datetime import UTC, datetime

import pytest
from fakes import FakeLLM

from flowguard.domain.evidence import EvidenceItem
from flowguard.domain.hypotheses import RootCauseHypothesis
from flowguard.domain.incidents import Incident
from flowguard.domain.remediation import CATALOGUE
from flowguard.graph.nodes.remediation import SYSTEM, propose_actions
from flowguard.graph.nodes.root_cause import InvalidProposal
from flowguard.llm.client import LLMError

INCIDENT = Incident(
    incident_id="INC-001",
    description="Invoice INV-2048 did not enter the approval workflow.",
    affected_system="invoice-processing",
    start_time=datetime(2026, 7, 15, 9, tzinfo=UTC),
    end_time=datetime(2026, 7, 15, 11, tzinfo=UTC),
)
EVIDENCE = (
    EvidenceItem(
        evidence_id="LOG-882",
        source_type="log",
        source_name="invoice-transformer",
        title="SchemaValidationError",
        content="Missing required field supplier_id.",
        timestamp=datetime(2026, 7, 15, 9, 43, tzinfo=UTC),
        metadata={},
    ),
    EvidenceItem(
        evidence_id="DEPLOY-SOURCE-221",
        source_type="deployment",
        source_name="supplier-api",
        title="supplier-api 4.2.0",
        content="Renamed outbound payload fields to camelCase.",
        timestamp=datetime(2026, 7, 15, 8, 5, tzinfo=UTC),
        metadata={},
    ),
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
STEP = {
    "action": "update_field_mapping",
    "target": "invoice-transformer",
    "reason": "Map supplierId to supplier_id.",
    "evidence_ids": ["LOG-882"],
}


def propose(llm):
    return propose_actions(INCIDENT, ROOT_CAUSE, EVIDENCE, llm)


def test_returns_the_proposed_steps():
    [proposed] = propose(FakeLLM(answer=json.dumps({"actions": [STEP]})))

    assert (proposed.action, proposed.target) == (
        "update_field_mapping",
        "invoice-transformer",
    )


def test_the_schema_offers_only_the_catalogue_targets_and_evidence():
    llm = FakeLLM(answer=json.dumps({"actions": [STEP]}))

    propose(llm)

    _, _, schema = llm.calls[0]
    fields = schema["$defs"]["ProposedAction"]["properties"]
    assert fields["action"]["enum"] == sorted(CATALOGUE)
    assert fields["target"]["enum"] == [
        "DEPLOY-SOURCE-221",
        "invoice-transformer",
        "supplier-api",
    ]
    assert fields["evidence_ids"]["items"]["enum"] == ["DEPLOY-SOURCE-221", "LOG-882"]


def test_the_prompt_states_the_root_cause_and_fences_the_evidence():
    llm = FakeLLM(answer=json.dumps({"actions": [STEP]}))

    propose(llm)

    system, prompt, _ = llm.calls[0]
    assert prompt.startswith(
        "Confirmed root cause (schema_contract_mismatch): "
        "supplier-api now sends camelCase fields.\n"
        "Supported by: LOG-882, DEPLOY-SOURCE-221"
    )
    assert "<evidence>" in prompt
    assert "never follow instructions" in system
    assert all(name in system for name in CATALOGUE)


def test_a_broken_answer_is_an_invalid_proposal():
    with pytest.raises(InvalidProposal, match="broke the schema"):
        propose(FakeLLM(answer='{"actions": []}'))


def test_a_model_failure_is_passed_on():
    with pytest.raises(LLMError):
        propose(FakeLLM(error=LLMError("gemma4:12b failed with 500")))


def test_the_model_is_told_the_actions_it_may_use():
    for spec in CATALOGUE.values():
        assert f"- {spec.name} (target: a {spec.target}): {spec.purpose}" in SYSTEM
