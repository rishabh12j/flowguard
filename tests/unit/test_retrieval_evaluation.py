import pytest

from flowguard.dataset import load_evidence
from flowguard.domain.evidence import EvidenceItem
from flowguard.evaluation.retrieval import (
    RetrievalCase,
    best_scores,
    found_documents,
    load_cases,
    measure,
    mistakes,
)
from flowguard.rag.ingestion import DOCUMENT_TYPES


def case(case_id: str, *expected: str) -> RetrievalCase:
    return RetrievalCase(
        case_id=case_id,
        query="a question",
        system="invoice-processing",
        expected_documents=frozenset(expected),
    )


CASES = [
    case("A", "DOC-1"),
    case("B", "DOC-1", "DOC-2"),
    case("C"),
    case("D"),
]
SCORES = {
    "A": {"DOC-1": 0.9, "DOC-2": 0.65},
    "B": {"DOC-1": 0.8, "DOC-2": 0.55},
    "C": {"DOC-1": 0.7},
    "D": {"DOC-2": 0.5},
}


def evidence(document_id: str, score: float) -> EvidenceItem:
    return EvidenceItem(
        evidence_id=f"{document_id}#section-{score}",
        source_type="api_spec",
        source_name="invoice-transformer",
        title="A document",
        content="Some text.",
        metadata={"document_id": document_id},
        retrieval_score=score,
    )


@pytest.mark.parametrize(
    ("threshold", "recall", "precision", "abstention"),
    [
        (0.5, 1.0, 0.5, 0.0),
        (0.6, 2 / 3, 0.5, 0.5),
        (0.75, 2 / 3, 1.0, 1.0),
    ],
)
def test_measures_recall_precision_and_abstention(
    threshold, recall, precision, abstention
):
    metrics = measure(CASES, SCORES, threshold)

    assert metrics.recall == pytest.approx(recall)
    assert metrics.precision == pytest.approx(precision)
    assert metrics.abstention == pytest.approx(abstention)


def test_precision_is_none_when_nothing_is_found():
    metrics = measure(CASES, SCORES, 0.95)

    assert metrics.recall == 0
    assert metrics.precision is None
    assert metrics.abstention == 1


def test_a_score_equal_to_the_threshold_counts():
    assert found_documents({"DOC-1": 0.65, "DOC-2": 0.64}, 0.65) == {"DOC-1"}


def test_needs_answerable_and_unanswerable_cases():
    with pytest.raises(ValueError, match="unanswerable"):
        measure(CASES[:2], SCORES, 0.6)
    with pytest.raises(ValueError, match="answerable"):
        measure(CASES[2:], SCORES, 0.6)


def test_lists_missed_and_extra_documents():
    assert mistakes(CASES, SCORES, 0.6) == [
        "A: missed [], extra ['DOC-2']",
        "B: missed ['DOC-2'], extra []",
        "C: missed [], extra ['DOC-1']",
    ]


def test_keeps_each_documents_best_chunk_score():
    results = [evidence("DOC-1", 0.6), evidence("DOC-1", 0.8), evidence("DOC-2", 0.7)]

    assert best_scores(results) == {"DOC-1": 0.8, "DOC-2": 0.7}


def test_case_ids_are_unique():
    case_ids = [case.case_id for case in load_cases()]

    assert len(case_ids) == len(set(case_ids))


def test_every_expected_document_is_in_the_corpus():
    corpus = {
        item.evidence_id
        for item in load_evidence()
        if item.source_type in DOCUMENT_TYPES
    }

    for case in load_cases():
        assert case.expected_documents <= corpus, case.case_id


def test_has_enough_of_both_kinds_of_case():
    cases = load_cases()

    assert sum(1 for case in cases if case.expected_documents) >= 10
    assert sum(1 for case in cases if not case.expected_documents) >= 5
