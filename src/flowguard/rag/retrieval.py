from qdrant_client import QdrantClient
from qdrant_client.models import FieldCondition, Filter, MatchValue, ScoredPoint

from flowguard.domain.evidence import EvidenceItem
from flowguard.rag.embedding import Embedder
from flowguard.rag.ingestion import COLLECTION

# Chosen with the retrieval evaluation (python -m flowguard.evaluation.retrieval).
# At 0.6, recall is 1.00 and abstention 0.71. 0.625 abstains more, but leaves the
# "disable validation" question only 0.003 above the threshold.
MIN_SCORE = 0.6

LIMIT = 5
METADATA_FIELDS = (
    "document_id",
    "system",
    "version",
    "effective_date",
    "section",
    "source_path",
    "is_current",
)


def current_documents_for(system: str) -> Filter:
    return Filter(
        must=[
            FieldCondition(key="system", match=MatchValue(value=system)),
            FieldCondition(key="is_current", match=MatchValue(value=True)),
        ]
    )


def to_score(cosine: float) -> float:
    # Cosine runs from -1 to 1, and identical texts can score just above 1.
    # Clamping keeps 0.45 meaning 0.45, where (cosine + 1) / 2 would make it 0.72.
    return min(max(cosine, 0.0), 1.0)


def to_evidence(point: ScoredPoint) -> EvidenceItem:
    if point.payload is None:
        raise ValueError(f"point {point.id} has no payload")
    payload = point.payload
    return EvidenceItem(
        evidence_id=payload["chunk_id"],
        source_type=payload["document_type"],
        source_name=payload["service"],
        title=payload["title"],
        content=payload["text"],
        metadata={field: payload[field] for field in METADATA_FIELDS},
        retrieval_score=to_score(point.score),
    )


def retrieve(
    query: str,
    embedder: Embedder,
    client: QdrantClient,
    *,
    system: str,
    limit: int = LIMIT,
    min_score: float = MIN_SCORE,
) -> list[EvidenceItem]:
    if not query.strip():
        raise ValueError("query must not be blank")
    if not system.strip():
        raise ValueError("system must not be blank")

    points = client.query_points(
        COLLECTION,
        query=embedder.embed_query(query),
        query_filter=current_documents_for(system),
        limit=limit,
    ).points
    return [to_evidence(point) for point in points if point.score >= min_score]
