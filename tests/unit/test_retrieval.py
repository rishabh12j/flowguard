import pytest
from fakes import FakeEmbedder
from qdrant_client import QdrantClient

from flowguard.dataset import load_evidence
from flowguard.rag.ingestion import ingest, knowledge_chunks
from flowguard.rag.retrieval import retrieve, to_score

CHUNKS = knowledge_chunks(load_evidence())
RUNBOOK = next(chunk for chunk in CHUNKS if chunk.document_id == "RB-SCHEMA-COMPAT")
STALE = RUNBOOK.model_copy(
    update={
        "chunk_id": "RB-SCHEMA-COMPAT-OLD#full-document",
        "is_current": False,
        "text": "Replay every failed message straight away.",
    }
)
OTHER_SYSTEM = RUNBOOK.model_copy(
    update={
        "chunk_id": "RB-PAYROLL#full-document",
        "system": "payroll",
        "text": "Rerun the payroll batch.",
    }
)
SYSTEM = "invoice-processing"


@pytest.fixture
def embedder():
    return FakeEmbedder()


@pytest.fixture
def client(embedder):
    client = QdrantClient(":memory:")
    ingest([*CHUNKS, STALE, OTHER_SYSTEM], embedder, client)
    return client


def ids(results) -> list[str]:
    return [item.evidence_id for item in results]


def test_returns_the_chunk_as_evidence_with_its_metadata(client, embedder):
    item = retrieve(RUNBOOK.text, embedder, client, system=SYSTEM)[0]

    assert item.evidence_id == RUNBOOK.chunk_id
    assert item.source_type == "runbook"
    assert item.source_name == RUNBOOK.service
    assert item.content == RUNBOOK.text
    assert item.metadata["source_path"] == RUNBOOK.source_path
    assert item.metadata["section"] == RUNBOOK.section


def test_every_result_keeps_its_own_document_type(client, embedder):
    results = retrieve(RUNBOOK.text, embedder, client, system=SYSTEM, min_score=0)

    assert {item.source_type for item in results} == {
        "api_spec",
        "runbook",
        "historical_incident",
    }


def test_an_exact_match_scores_one(client, embedder):
    item = retrieve(RUNBOOK.text, embedder, client, system=SYSTEM)[0]

    assert item.retrieval_score == pytest.approx(1)


def test_results_come_best_first(client, embedder):
    results = retrieve(RUNBOOK.text, embedder, client, system=SYSTEM, min_score=0)

    scores = [item.retrieval_score for item in results]
    assert scores == sorted(scores, reverse=True)


def test_drops_results_below_the_threshold(client, embedder):
    results = retrieve(RUNBOOK.text, embedder, client, system=SYSTEM, min_score=0.999)

    assert ids(results) == [RUNBOOK.chunk_id]


def test_nothing_above_the_threshold_is_an_empty_result(client, embedder):
    results = retrieve(
        "best recipe for chocolate cake",
        embedder,
        client,
        system=SYSTEM,
        min_score=0.999,
    )

    assert results == []


def test_returns_at_most_the_limit(client, embedder):
    results = retrieve(
        RUNBOOK.text, embedder, client, system=SYSTEM, limit=2, min_score=0
    )

    assert len(results) == 2


def test_never_returns_a_stale_document(client, embedder):
    results = retrieve(STALE.text, embedder, client, system=SYSTEM, min_score=0)

    assert STALE.chunk_id not in ids(results)
    assert len(results) == len(CHUNKS)


def test_stale_documents_do_not_use_up_the_limit(client, embedder):
    results = retrieve(
        STALE.text, embedder, client, system=SYSTEM, limit=1, min_score=0
    )

    assert len(results) == 1
    assert results[0].metadata["is_current"] is True


def test_never_returns_another_systems_document(client, embedder):
    results = retrieve(OTHER_SYSTEM.text, embedder, client, system=SYSTEM, min_score=0)

    assert OTHER_SYSTEM.chunk_id not in ids(results)


@pytest.mark.parametrize("query", ["", "   "])
def test_rejects_a_blank_query(client, embedder, query):
    with pytest.raises(ValueError, match="query"):
        retrieve(query, embedder, client, system=SYSTEM)


def test_rejects_a_blank_system(client, embedder):
    with pytest.raises(ValueError, match="system"):
        retrieve(RUNBOOK.text, embedder, client, system=" ")


@pytest.mark.parametrize(
    ("cosine", "expected"),
    [(-0.3, 0.0), (0.0, 0.0), (0.45, 0.45), (1.0000000432693739, 1.0)],
)
def test_to_score_keeps_the_meaning_and_stays_in_range(cosine, expected):
    assert to_score(cosine) == expected
