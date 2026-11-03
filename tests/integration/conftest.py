import pytest
from qdrant_client import QdrantClient

from flowguard.dataset import load_evidence
from flowguard.rag.embedding import SentenceTransformerEmbedder
from flowguard.rag.ingestion import ingest, knowledge_chunks


@pytest.fixture(scope="session")
def embedder():
    return SentenceTransformerEmbedder()


@pytest.fixture(scope="session")
def client(embedder):
    client = QdrantClient(":memory:")
    ingest(knowledge_chunks(load_evidence()), embedder, client)
    return client
