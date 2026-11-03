import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from flowguard.domain.evidence import EvidenceItem
from flowguard.rag.chunking import Chunk, chunk_document
from flowguard.rag.embedding import Embedder

COLLECTION = "knowledge"
DOCUMENT_TYPES = {"api_spec", "runbook", "historical_incident"}


def knowledge_chunks(evidence: list[EvidenceItem]) -> list[Chunk]:
    return [
        chunk
        for item in evidence
        if item.source_type in DOCUMENT_TYPES
        for chunk in chunk_document(item)
    ]


def point_id(chunk_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, chunk_id))


def ingest(chunks: list[Chunk], embedder: Embedder, client: QdrantClient) -> None:
    for chunk in chunks:
        tokens = embedder.count_tokens(chunk.text)
        if tokens > embedder.max_tokens:
            raise ValueError(
                f"{chunk.chunk_id} has {tokens} tokens, "
                f"but the model reads {embedder.max_tokens}"
            )

    vectors = embedder.embed_documents([chunk.text for chunk in chunks])

    if client.collection_exists(COLLECTION):
        client.delete_collection(COLLECTION)
    client.create_collection(
        COLLECTION,
        vectors_config=VectorParams(size=embedder.dimensions, distance=Distance.COSINE),
    )
    client.upsert(
        COLLECTION,
        points=[
            PointStruct(
                id=point_id(chunk.chunk_id),
                vector=vector,
                payload=chunk.model_dump(),
            )
            for chunk, vector in zip(chunks, vectors)
        ],
    )
