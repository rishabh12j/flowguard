"""Proves INC-001 can be solved from its evidence without an LLM.

Delete this file once the investigation graph solves INC-001.
"""

import json
import re

from flowguard.dataset import DATA_DIR, load_evidence, load_incident
from flowguard.domain.evidence import EvidenceItem


def by_type(evidence: list[EvidenceItem], source_type: str) -> list[EvidenceItem]:
    return [item for item in evidence if item.source_type == source_type]


def find_transaction(incident: dict, evidence: list[EvidenceItem]) -> str:
    invoice_id = re.search(r"INV-\d+", incident["description"]).group()
    logs = by_type(evidence, "log")
    return next(i.correlation_id for i in logs if i.metadata.get("invoice_id") == invoice_id)


def find_first_failure(evidence: list[EvidenceItem], correlation_id: str) -> EvidenceItem:
    errors = [
        item
        for item in by_type(evidence, "log")
        if item.correlation_id == correlation_id and item.metadata["level"] == "ERROR"
    ]
    return min(errors, key=lambda item: item.timestamp)


def services_at_or_before(evidence: list[EvidenceItem], service: str) -> set[str]:
    edges = by_type(evidence, "dependency_map")[0].metadata["edges"]
    found = {service}
    frontier = {service}
    while frontier:
        frontier = {edge["from"] for edge in edges if edge["to"] in frontier} - found
        found |= frontier
    return found


def last_success_from_source(evidence: list[EvidenceItem], source_system: str):
    logs = by_type(evidence, "log")
    completed = {i.correlation_id for i in logs if i.source_name == "invoice-workflow"}
    return max(
        item.timestamp
        for item in logs
        if item.correlation_id in completed and item.metadata.get("source_system") == source_system
    )


def find_suspect_deployments(evidence: list[EvidenceItem], failure: EvidenceItem) -> list[EvidenceItem]:
    possible_services = services_at_or_before(evidence, failure.source_name)
    last_success = last_success_from_source(evidence, failure.metadata["source_system"])
    return [
        item
        for item in by_type(evidence, "deployment")
        if item.source_name in possible_services and last_success < item.timestamp < failure.timestamp
    ]


def compare_with_contract(
    evidence: list[EvidenceItem], failure: EvidenceItem
) -> tuple[EvidenceItem, set[str], set[str]]:
    spec = next(i for i in by_type(evidence, "api_spec") if i.source_name == failure.source_name)
    required = set(re.findall(r"^\| `(\w+)` \| \w+ \| Yes", spec.content, re.MULTILINE))
    received = next(
        set(item.metadata["received_fields"])
        for item in by_type(evidence, "log")
        if item.correlation_id == failure.correlation_id and "received_fields" in item.metadata
    )
    return spec, required - received, received - required


def solve(incident: dict, evidence: list[EvidenceItem]) -> dict:
    correlation_id = find_transaction(incident, evidence)
    failure = find_first_failure(evidence, correlation_id)
    deployments = find_suspect_deployments(evidence, failure)
    spec, missing, unexpected = compare_with_contract(evidence, failure)

    is_schema_mismatch = failure.metadata["exception_type"] == "SchemaValidationError"
    category = "schema_contract_mismatch" if is_schema_mismatch and missing else "unknown"
    return {
        "category": category,
        "missing_fields": missing,
        "unexpected_fields": unexpected,
        "evidence_ids": {failure.evidence_id, spec.evidence_id, *(d.evidence_id for d in deployments)},
    }


def test_inc_001_can_be_solved_from_the_evidence():
    ground_truth = json.loads((DATA_DIR / "ground_truth" / "INC-001.json").read_text(encoding="utf-8"))

    result = solve(load_incident("INC-001"), load_evidence())

    assert result["category"] == ground_truth["category"]
    assert result["evidence_ids"] == set(ground_truth["required_evidence_ids"])
    assert result["missing_fields"] == {"supplier_id", "total_amount"}
    assert result["unexpected_fields"] == {"supplierId", "invoiceTotal"}
