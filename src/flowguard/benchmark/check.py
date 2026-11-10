"""Checks the benchmark is sound before any model sees it.

    python -m flowguard.benchmark.check --data-dir data/benchmark

Every incident must load, keep its evidence unchanged by redaction, stay isolated
from the others in time, and be solved by the oracle through the real graph:
the right category at 0.65 or above with the reference plan, or an abstention.
A cause with no change before it can't reach 0.65 under the rubric, so for one
the oracle must gather the required evidence and propose the right category,
and its reference plan must pass validation on the evidence gathered. Every
prompt must also fit in the model's context.
"""

import argparse
import asyncio
from collections import Counter
from datetime import timedelta
from functools import partial
from pathlib import Path
from typing import Any

from qdrant_client import QdrantClient

from flowguard.dataset import (
    incident_ids,
    load_evidence,
    load_ground_truth,
    load_incident,
)
from flowguard.domain.audit import InvestigationRecord
from flowguard.domain.causality import LOOKBACK
from flowguard.domain.evidence import EvidenceItem
from flowguard.domain.incidents import Incident
from flowguard.domain.redaction import redact_evidence
from flowguard.domain.remediation import ProposedAction
from flowguard.domain.validation import check_actions
from flowguard.evaluation.investigations import run_incident
from flowguard.evaluation.oracle import Oracle
from flowguard.graph.nodes.root_cause import MIN_CONFIDENCE
from flowguard.rag.embedding import SentenceTransformerEmbedder
from flowguard.rag.ingestion import ingest, knowledge_chunks
from flowguard.rag.retrieval import retrieve
from flowguard.seed_schemas import GroundTruth

# Ollama is given 8,192 tokens. About 3.5 characters a token for this text, with
# room left for the answer.
MAX_PROMPT_CHARACTERS = 24_000
CHANGES = ("deployment", "alert", "metric")


class MeasuredOracle(Oracle):
    """The oracle, keeping the size of the largest prompt it was sent."""

    def __init__(self, truth: GroundTruth) -> None:
        super().__init__(truth)
        self.largest = 0

    def generate(self, system: str, prompt: str, schema: dict[str, Any]) -> str:
        self.largest = max(self.largest, len(system) + len(prompt))
        return super().generate(system, prompt, schema)


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
    support = selected.support if selected.support is not None else 0.0
    if support < MIN_CONFIDENCE:
        problems.append(f"support {support}")
    planned = [{"action": a.action, "target": a.target} for a in record.actions]
    if planned != [step.model_dump() for step in truth.reference_plan]:
        problems.append(f"plan {planned}")
    if record.rejected_actions:
        problems.append(f"refused: {[r.problem for r in record.rejected_actions]}")
    expected = "awaiting_approval" if truth.expected_approval_required else "diagnosed"
    if record.status != expected:
        problems.append(f"status {record.status}, expected {expected}")
    return problems


def solved_without_change(
    record: InvestigationRecord,
    truth: GroundTruth,
    by_id: dict[str, EvidenceItem],
) -> list[str]:
    """What's wrong with the oracle's result for a cause with no change before it."""
    if record.selected_hypothesis_id is not None:
        return solved(record, truth)
    found = {item.split("#")[0] for item in record.evidence_ids}
    missing = sorted(set(truth.required_evidence_ids) - found)
    if missing:
        return [f"required evidence not gathered: {missing}"]
    if not record.hypotheses or record.hypotheses[0].category != truth.category:
        return ["the oracle's hypothesis wasn't recorded with the right category"]
    gathered = [by_id[i] for i in record.evidence_ids if i in by_id]
    proposed = [
        ProposedAction(
            action=step.action,
            target=step.target,
            reason="From the runbook.",
            evidence_ids=(truth.required_evidence_ids[0],),
        )
        for step in truth.reference_plan
    ]
    _, rejected = check_actions(proposed, gathered, record.hypotheses[0])
    return [f"plan refused: {[r.problem for r in rejected]}"] if rejected else []


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
    by_id = {item.evidence_id: item for item in evidence}
    largest = 0
    for number, incident_id in enumerate(incidents, start=1):
        truth = truths[incident_id]
        oracle = MeasuredOracle(truth)
        record, _ = await run_incident(
            incident_id, oracle, search, data_dir=data_dir, evidence=evidence
        )
        largest = max(largest, oracle.largest)
        if oracle.largest > MAX_PROMPT_CHARACTERS:
            problems.append(
                f"{incident_id}: a prompt of {oracle.largest} characters may not "
                "fit the model's context"
            )
        change_required = any(
            i in by_id and by_id[i].source_type in CHANGES
            for i in truth.required_evidence_ids
        )
        if truth.expected_outcome == "diagnose" and not change_required:
            found = solved_without_change(record, truth, by_id)
        else:
            found = solved(record, truth)
        for problem in found:
            problems.append(f"{incident_id} ({truth.family}): {problem}")
        if number % 50 == 0:
            print(f"checked {number} of {len(incidents)}", flush=True)
    print(f"largest prompt: {largest} characters", flush=True)
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
