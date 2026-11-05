"""Checks the benchmark is sound before any model sees it.

    python -m flowguard.benchmark.check --data-dir data/benchmark

Every incident must load, keep its evidence unchanged by redaction, stay isolated
from the others in time, and be solved by the oracle through the real graph:
the right category at 0.65 or above with the reference plan, or an abstention.
"""

import argparse
import asyncio
from collections import Counter
from datetime import timedelta
from functools import partial
from pathlib import Path

from qdrant_client import QdrantClient

from flowguard.dataset import (
    incident_ids,
    load_evidence,
    load_ground_truth,
    load_incident,
)
from flowguard.domain.audit import InvestigationRecord
from flowguard.domain.causality import LOOKBACK
from flowguard.domain.incidents import Incident
from flowguard.domain.redaction import redact_evidence
from flowguard.evaluation.investigations import run_incident
from flowguard.evaluation.oracle import Oracle
from flowguard.graph.nodes.root_cause import MIN_CONFIDENCE
from flowguard.rag.embedding import SentenceTransformerEmbedder
from flowguard.rag.ingestion import ingest, knowledge_chunks
from flowguard.rag.retrieval import retrieve
from flowguard.seed_schemas import GroundTruth


def solved(record: InvestigationRecord, truth: GroundTruth) -> list[str]:
    """What's wrong with the oracle's result, if anything."""
    if truth.expected_outcome == "abstain":
        return (
            []
            if record.status == "abstained"
            else [f"should abstain, got {record.status}"]
        )
    problems = []
    found = {item.split("#")[0] for item in record.evidence_ids}
    missing = sorted(set(truth.required_evidence_ids) - found)
    if missing:
        problems.append(f"required evidence not gathered: {missing}")
    selected = next(
        (
            h
            for h in record.hypotheses
            if h.hypothesis_id == record.selected_hypothesis_id
        ),
        None,
    )
    if selected is None:
        problems.append(f"nothing selected: {record.abstention}")
        return problems
    if record.category != truth.category:
        problems.append(f"category {record.category}, expected {truth.category}")
    if selected.confidence < MIN_CONFIDENCE:
        problems.append(f"confidence {selected.confidence}")
    planned = [{"action": a.action, "target": a.target} for a in record.actions]
    if planned != [step.model_dump() for step in truth.reference_plan]:
        problems.append(f"plan {planned}")
    if record.rejected_actions:
        problems.append(f"refused: {[r.problem for r in record.rejected_actions]}")
    expected = "awaiting_approval" if truth.expected_approval_required else "diagnosed"
    if record.status != expected:
        problems.append(f"status {record.status}, expected {expected}")
    return problems


async def check(data_dir: Path) -> list[str]:
    problems: list[str] = []
    evidence = load_evidence(data_dir)
    counts = Counter(item.evidence_id for item in evidence)
    problems += [f"{key} appears {n} times" for key, n in counts.items() if n > 1]
    problems += [
        f"{item.evidence_id} would be changed by redaction"
        for item in evidence
        if redact_evidence(item) != item
    ]

    incidents = incident_ids(data_dir)
    truths = {
        incident_id: load_ground_truth(incident_id, data_dir)
        for incident_id in incidents
    }
    windows = sorted(
        (Incident.model_validate(load_incident(i, data_dir)).start_time, i)
        for i in incidents
    )
    ends = {
        i: Incident.model_validate(load_incident(i, data_dir)).end_time
        for i in incidents
    }
    for (_, previous), (start, current) in zip(windows, windows[1:], strict=False):
        # The next incident's lookback mustn't reach back into this one.
        if start - LOOKBACK - timedelta(hours=1) <= ends[previous]:
            problems.append(f"{current} is too close to {previous}")

    embedder = SentenceTransformerEmbedder()
    client = QdrantClient(":memory:")
    ingest(knowledge_chunks(evidence), embedder, client)
    search = partial(retrieve, embedder=embedder, client=client)
    for number, incident_id in enumerate(incidents, start=1):
        truth = truths[incident_id]
        record, _ = await run_incident(
            incident_id, Oracle(truth), search, data_dir=data_dir, evidence=evidence
        )
        for problem in solved(record, truth):
            problems.append(f"{incident_id} ({truth.family}): {problem}")
        if number % 50 == 0:
            print(f"checked {number} of {len(incidents)}", flush=True)
    return problems


def main() -> None:
    parser = argparse.ArgumentParser(description="Check FlowGuard's benchmark.")
    parser.add_argument("--data-dir", type=Path, default=Path("data/benchmark"))
    problems = asyncio.run(check(parser.parse_args().data_dir))
    for problem in problems:
        print(problem)
    print(f"{len(problems)} problems")
    if problems:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
