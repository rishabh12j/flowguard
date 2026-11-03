import pytest

from flowguard.evaluation.retrieval import collect_scores, load_cases, measure
from flowguard.rag.retrieval import MIN_SCORE

CASES = load_cases()


@pytest.fixture(scope="module")
def scores(client, embedder):
    return collect_scores(CASES, embedder, client)


def test_scores_include_results_below_the_threshold(scores):
    # The sweep needs every score, not only those retrieve would keep. RET-014
    # is the chocolate cake question, which scores below every threshold tried.
    assert scores["RET-014"]


def test_min_score_finds_every_expected_document(scores):
    assert measure(CASES, scores, MIN_SCORE).recall == 1


def test_min_score_abstains_on_most_unanswerable_questions(scores):
    # Measured at 0.71 when MIN_SCORE was chosen. A lower value means the model,
    # the documents, or the threshold changed, and the threshold needs re-tuning.
    assert measure(CASES, scores, MIN_SCORE).abstention >= 0.7
