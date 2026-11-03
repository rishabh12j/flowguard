import hashlib

import pytest
from qdrant_client import QdrantClient
from qdrant_client.models import Distance

from flowguard.dataset import load_evidence
from flowguard.rag.ingestion import COLLECTION, ingest, knowledge_chunks, point_id

CHUNKS = knowledge_chunks(load_evidence())


class FakeEmbedder:
    """Gives repeatable vectors without loading a real model."""

    dimensions = 4
    max_tokens = 1000

    def count_tokens(self, text: str) -> int:
        return len(text.split())

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_query(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode()).digest()
        return [byte / 255 + 0.01 for byte in digest[:4]]


@pytest.fixture
def client():
    return QdrantClient(":memory:")


def count(client) -> int:
    return client.count(COLLECTION).count


def test_only_knowledge_documents_become_chunks():
    assert {chunk.document_type for chunk in CHUNKS} == {
        "api_spec",
        "runbook",
        "historical_incident",
    }
    assert len(CHUNKS) == 4


def test_stores_one_point_per_chunk(client):
    ingest(CHUNKS, FakeEmbedder(), client)

    assert count(client) == 4


def test_collection_uses_cosine_and_the_model_size(client):
    ingest(CHUNKS, FakeEmbedder(), client)

    vectors = client.get_collection(COLLECTION).config.params.vectors
    assert vectors.size == FakeEmbedder.dimensions
    assert vectors.distance == Distance.COSINE


def test_payload_keeps_the_text_and_metadata(client):
    ingest(CHUNKS, FakeEmbedder(), client)

    chunk = CHUNKS[0]
    point = client.retrieve(COLLECTION, [point_id(chunk.chunk_id)])[0]
    assert point.payload == chunk.model_dump()


def test_a_chunk_can_be_found_by_its_vector(client):
    embedder = FakeEmbedder()
    ingest(CHUNKS, embedder, client)

    chunk = CHUNKS[1]
    found = client.query_points(
        COLLECTION, query=embedder.embed_query(chunk.text), limit=1
    ).points[0]
    assert found.payload["chunk_id"] == chunk.chunk_id


def test_point_ids_stay_the_same_between_runs():
    assert point_id("RB-SCHEMA-COMPAT#full-document") == point_id(
        "RB-SCHEMA-COMPAT#full-document"
    )


def test_ingesting_twice_does_not_duplicate(client):
    ingest(CHUNKS, FakeEmbedder(), client)
    ingest(CHUNKS, FakeEmbedder(), client)

    assert count(client) == 4


def test_a_removed_document_does_not_stay_searchable(client):
    ingest(CHUNKS, FakeEmbedder(), client)
    ingest(CHUNKS[:1], FakeEmbedder(), client)

    assert count(client) == 1


def test_rejects_a_chunk_the_model_would_cut_off(client):
    embedder = FakeEmbedder()
    embedder.max_tokens = 3

    with pytest.raises(ValueError, match="tokens"):
        ingest(CHUNKS, embedder, client)


def test_a_rejected_ingest_keeps_the_existing_collection(client):
    ingest(CHUNKS, FakeEmbedder(), client)
    embedder = FakeEmbedder()
    embedder.max_tokens = 3

    with pytest.raises(ValueError):
        ingest(CHUNKS, embedder, client)

    assert count(client) == 4
