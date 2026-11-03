import math

import pytest
from qdrant_client import QdrantClient


from flowguard.dataset import load_evidence, load_incident

from flowguard.rag.ingestion import COLLECTION, ingest, knowledge_chunks
from flowguard.rag.retrieval import retrieve
from flowguard.rag.embedding import SentenceTransformerEmbedder


CHUNKS = knowledge_chunks(load_evidence())


@pytest.fixture(scope="module")
def embedder():
    return SentenceTransformerEmbedder()


@pytest.fixture(scope="module")
def client(embedder):
    client = QdrantClient(":memory:")
    ingest(CHUNKS, embedder, client)
    return client


def top_chunk(client, embedder, query):
    vector = embedder.embed_query(query)
    return client.query_points(COLLECTION, query=vector, limit=1).points[0]


def test_reports_the_model_size(embedder):
    assert embedder.dimensions == 384
    assert embedder.max_tokens == 512


def test_vectors_have_the_reported_size_and_length_one(embedder):
    vector = embedder.embed_query("schema mismatch")

    assert len(vector) == embedder.dimensions
    assert math.sqrt(sum(value * value for value in vector)) == pytest.approx(1)


def test_the_same_text_gives_the_same_vector(embedder):
    assert embedder.embed_query("schema mismatch") == embedder.embed_query(
        "schema mismatch"
    )


def test_counts_tokens_without_cutting_long_text(embedder):
    assert embedder.count_tokens("word " * 1000) > embedder.max_tokens


def test_every_inc_001_chunk_fits_the_model(embedder):
    assert all(
        embedder.count_tokens(chunk.text) <= embedder.max_tokens for chunk in CHUNKS
    )


def test_finds_the_runbook_from_its_warnings(client, embedder):
    found = top_chunk(
        client, embedder, "can I disable payload validation to clear the queue"
    )

    assert found.payload["document_id"] == "RB-SCHEMA-COMPAT"


def test_finds_the_past_incident_from_its_symptoms(client, embedder):
    found = top_chunk(
        client,
        embedder,
        "invoices stopped reaching the workflow while the source returned success",
    )

    assert found.payload["document_id"] == "HIST-INC-044"


def test_inc_001_retrieves_the_past_incident_and_the_runbook(client, embedder):
    incident = load_incident("INC-001")

    results = retrieve(
        incident["description"],
        embedder,
        client,
        system=incident["affected_system"],
    )

    documents = {item.metadata["document_id"] for item in results}
    assert {"HIST-INC-044", "RB-SCHEMA-COMPAT"} <= documents


@pytest.mark.parametrize(
    "query",
    ["best recipe for chocolate cake", "pod restarted after running out of memory"],
)
def test_an_unrelated_question_finds_nothing(client, embedder, query):
    assert retrieve(query, embedder, client, system="invoice-processing") == []


def test_an_exact_match_does_not_score_above_one(client, embedder):
    runbook = next(chunk for chunk in CHUNKS if chunk.document_id == "RB-SCHEMA-COMPAT")

    item = retrieve(runbook.text, embedder, client, system="invoice-processing")[0]

    assert item.retrieval_score == 1

