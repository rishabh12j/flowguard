import pytest
from pydantic import ValidationError

from flowguard.domain.hypotheses import (
    HypothesisProposal,
    ProposedHypothesis,
    CATEGORY_DEFINITIONS,
    IncidentCategory,
)
from typing import get_args


def hypothesis(**changes) -> dict:
    return {
        "description": "The mapping still expects snake_case fields.",
        "supporting_evidence_ids": ["LOG-882"],
        "contradicting_evidence_ids": [],
        "missing_evidence": [],
        "category": "schema_contract_mismatch",
        **changes,
    }


def test_accepts_a_hypothesis_with_evidence():
    proposed = ProposedHypothesis.model_validate(hypothesis())

    assert proposed.supporting_evidence_ids == ("LOG-882",)


def test_needs_supporting_evidence():
    with pytest.raises(ValidationError, match="supporting_evidence_ids"):
        ProposedHypothesis.model_validate(hypothesis(supporting_evidence_ids=[]))


def test_evidence_cannot_both_support_and_contradict():
    with pytest.raises(ValidationError, match="both supports and contradicts"):
        ProposedHypothesis.model_validate(
            hypothesis(contradicting_evidence_ids=["LOG-882"])
        )


def test_rejects_a_blank_description():
    with pytest.raises(ValidationError, match="description"):
        ProposedHypothesis.model_validate(hypothesis(description=""))


def test_rejects_a_confidence_from_the_model():
    with pytest.raises(ValidationError, match="confidence"):
        ProposedHypothesis.model_validate(hypothesis(confidence=0.99))


@pytest.mark.parametrize("count", [0, 4])
def test_a_proposal_has_one_to_three_hypotheses(count):
    with pytest.raises(ValidationError, match="hypotheses"):
        HypothesisProposal.model_validate({"hypotheses": [hypothesis()] * count})


def test_rejects_a_category_outside_the_list():
    with pytest.raises(ValidationError, match="category"):
        ProposedHypothesis.model_validate(hypothesis(category="database"))


def test_needs_a_category():
    proposed = hypothesis()
    del proposed["category"]

    with pytest.raises(ValidationError, match="category"):
        ProposedHypothesis.model_validate(proposed)


def test_every_category_has_a_definition():
    assert set(CATEGORY_DEFINITIONS) == set(get_args(IncidentCategory))
