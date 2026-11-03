import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field
from qdrant_client import QdrantClient

from flowguard.dataset import DATA_DIR, load_evidence
from flowguard.domain.evidence import EvidenceItem
from flowguard.rag.embedding import Embedder, SentenceTransformerEmbedder
from flowguard.rag.ingestion import ingest, knowledge_chunks
from flowguard.rag.retrieval import MIN_SCORE, retrieve

CASES_PATH = DATA_DIR / "evaluation" / "retrieval_cases.json"
THRESHOLDS = [round(0.5 + step * 0.025, 3) for step in range(11)]


class RetrievalCase(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    case_id: str = Field(pattern=r"^\S+$")
    query: str = Field(min_length=1)
    system: str
    # Empty means nothing in the corpus answers the query, so retrieval should abstain.
    expected_documents: frozenset[str]


class RetrievalMetrics(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    threshold: float
    recall: float
    precision: float | None
    abstention: float


def load_cases(path: Path = CASES_PATH) -> list[RetrievalCase]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [RetrievalCase.model_validate(case) for case in raw]


def best_scores(results: list[EvidenceItem]) -> dict[str, float]:
    # A document can return several chunks, so keep each document's best score.
    scores: dict[str, float] = {}
    for item in results:
        document = item.metadata["document_id"]
        scores[document] = max(scores.get(document, 0.0), item.retrieval_score or 0.0)
    return scores


def collect_scores(
    cases: list[RetrievalCase], embedder: Embedder, client: QdrantClient
) -> dict[str, dict[str, float]]:
    # Search once with no threshold, so every threshold can be measured from the same scores.
    return {
        case.case_id: best_scores(
            retrieve(case.query, embedder, client, system=case.system, min_score=0)
        )
        for case in cases
    }


def found_documents(scores: dict[str, float], threshold: float) -> set[str]:
    return {document for document, score in scores.items() if score >= threshold}


def measure(
    cases: list[RetrievalCase],
    scores_by_case: dict[str, dict[str, float]],
    threshold: float,
) -> RetrievalMetrics:
    answerable = [case for case in cases if case.expected_documents]
    unanswerable = [case for case in cases if not case.expected_documents]
    if not answerable or not unanswerable:
        raise ValueError("cases need both answerable and unanswerable questions")

    found = {
        case.case_id: found_documents(scores_by_case[case.case_id], threshold)
        for case in cases
    }
    correct = sum(len(found[case.case_id] & case.expected_documents) for case in cases)
    expected = sum(len(case.expected_documents) for case in answerable)
    returned = sum(len(documents) for documents in found.values())
    abstained = sum(not found[case.case_id] for case in unanswerable)

    return RetrievalMetrics(
        threshold=threshold,
        recall=correct / expected,
        precision=correct / returned if returned else None,
        abstention=abstained / len(unanswerable),
    )


def mistakes(
    cases: list[RetrievalCase],
    scores_by_case: dict[str, dict[str, float]],
    threshold: float,
) -> list[str]:
    lines = []
    for case in cases:
        found = found_documents(scores_by_case[case.case_id], threshold)
        missed = sorted(case.expected_documents - found)
        extra = sorted(found - case.expected_documents)
        if missed or extra:
            lines.append(f"{case.case_id}: missed {missed}, extra {extra}")
    return lines


def main() -> None:
    embedder = SentenceTransformerEmbedder()
    client = QdrantClient(":memory:")
    ingest(knowledge_chunks(load_evidence()), embedder, client)
    cases = load_cases()
    scores_by_case = collect_scores(cases, embedder, client)

    print("threshold  recall  precision  abstention")
    for threshold in THRESHOLDS:
        metrics = measure(cases, scores_by_case, threshold)
        precision = "-" if metrics.precision is None else f"{metrics.precision:.2f}"
        print(
            f"{threshold:9.3f}  {metrics.recall:6.2f}  {precision:>9}  "
            f"{metrics.abstention:10.2f}"
        )

    print(f"\nMistakes at MIN_SCORE = {MIN_SCORE}:")
    for line in mistakes(cases, scores_by_case, MIN_SCORE) or ["none"]:
        print(f"  {line}")


if __name__ == "__main__":
    main()
