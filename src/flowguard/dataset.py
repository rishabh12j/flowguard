import json
from pathlib import Path
from typing import Any

from flowguard.domain.evidence import EvidenceItem, SourceType

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

DOCUMENT_FOLDERS: dict[str, SourceType] = {
    "api_specs": "api_spec",
    "runbooks": "runbook",
    "historical_incidents": "historical_incident",
}


def load_incident(incident_id: str, data_dir: Path = DATA_DIR) -> dict[str, Any]:
    return _read_json(data_dir / "incidents" / f"{incident_id}.json")


def load_evidence(data_dir: Path = DATA_DIR) -> list[EvidenceItem]:
    return [
        *_load_logs(data_dir),
        *_load_deployments(data_dir),
        *_load_dependency_maps(data_dir),
        *_load_documents(data_dir),
    ]


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_logs(data_dir: Path) -> list[EvidenceItem]:
    items = []
    for path in sorted((data_dir / "logs").glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            items.append(_log_to_evidence(json.loads(line)))
    return items


def _log_to_evidence(event: dict[str, Any]) -> EvidenceItem:
    return EvidenceItem(
        evidence_id=event["event_id"],
        source_type="log",
        source_name=event["service"],
        timestamp=event["timestamp"],
        title=event["exception_type"] or f"{event['level']} event",
        content=event["message"],
        metadata={
            "level": event["level"],
            "environment": event["environment"],
            "exception_type": event["exception_type"],
            **event["metadata"],
        },
        correlation_id=event["correlation_id"],
    )


def _load_deployments(data_dir: Path) -> list[EvidenceItem]:
    items = []
    for path in sorted((data_dir / "deployments").glob("*.json")):
        for record in _read_json(path):
            items.append(
                EvidenceItem(
                    evidence_id=record["deployment_id"],
                    source_type="deployment",
                    source_name=record["service"],
                    timestamp=record["timestamp"],
                    title=f"{record['service']} {record['version']} deployment",
                    content="\n".join(record["changes"]),
                    metadata={"version": record["version"], "status": record["status"]},
                )
            )
    return items


def _load_dependency_maps(data_dir: Path) -> list[EvidenceItem]:
    items = []
    for path in sorted((data_dir / "dependency_maps").glob("*.json")):
        record = _read_json(path)
        items.append(
            EvidenceItem(
                evidence_id=record["map_id"],
                source_type="dependency_map",
                source_name=record["system"],
                title=f"{record['system']} dependency map",
                content="\n".join(f"{edge['from']} -> {edge['to']}" for edge in record["edges"]),
                metadata={"nodes": record["nodes"], "edges": record["edges"]},
            )
        )
    return items


def _load_documents(data_dir: Path) -> list[EvidenceItem]:
    items = []
    for folder, source_type in DOCUMENT_FOLDERS.items():
        for path in sorted((data_dir / folder).glob("*.md")):
            metadata, body = _split_front_matter(path.read_text(encoding="utf-8"))
            metadata["source_path"] = path.relative_to(data_dir).as_posix()
            items.append(
                EvidenceItem(
                    evidence_id=metadata["document_id"],
                    source_type=source_type,
                    source_name=metadata["service"],
                    title=metadata["title"],
                    content=body,
                    metadata=metadata,
                )
            )
    return items


def _split_front_matter(text: str) -> tuple[dict[str, Any], str]:
    _, header, body = text.split("---", 2)
    metadata: dict[str, Any] = {}
    for line in header.strip().splitlines():
        key, value = line.split(": ", 1)
        metadata[key] = value
    metadata["is_current"] = metadata["is_current"] == "true"
    return metadata, body.strip()
