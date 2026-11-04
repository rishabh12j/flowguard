import json
from pathlib import Path
from typing import Any

from flowguard.domain.evidence import EvidenceItem, SourceType
from flowguard.domain.metrics import metric_evidence
from flowguard.seed_schemas import (
    AlertRecord,
    DependencyMapRecord,
    DeploymentRecord,
    DocumentHeader,
    GroundTruth,
    LogRecord,
    MetricSeries,
)

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

DOCUMENT_FOLDERS: dict[str, SourceType] = {
    "api_specs": "api_spec",
    "runbooks": "runbook",
    "historical_incidents": "historical_incident",
}


def load_incident(incident_id: str, data_dir: Path = DATA_DIR) -> dict[str, Any]:
    # Kept as the raw request: the investigation validates it, and audits a rejection.
    return _read_json(data_dir / "incidents" / f"{incident_id}.json")


def load_ground_truth(incident_id: str, data_dir: Path = DATA_DIR) -> GroundTruth:
    return GroundTruth.model_validate(
        _read_json(data_dir / "ground_truth" / f"{incident_id}.json")
    )


def incident_ids(data_dir: Path = DATA_DIR) -> list[str]:
    return sorted(path.stem for path in (data_dir / "incidents").glob("*.json"))


def load_evidence(data_dir: Path = DATA_DIR) -> list[EvidenceItem]:
    return [
        *_load_logs(data_dir),
        *_load_deployments(data_dir),
        *_load_alerts(data_dir),
        *_load_metrics(data_dir),
        *_load_dependency_maps(data_dir),
        *_load_documents(data_dir),
    ]


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_logs(data_dir: Path) -> list[EvidenceItem]:
    items = []
    for path in sorted((data_dir / "logs").glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            record = LogRecord.model_validate_json(line)
            items.append(_log_to_evidence(record, system=path.stem))
    return items


def _log_to_evidence(event: LogRecord, system: str) -> EvidenceItem:
    return EvidenceItem(
        evidence_id=event.event_id,
        source_type="log",
        source_name=event.service,
        timestamp=event.timestamp,
        title=event.exception_type or f"{event.level} event",
        content=event.message,
        metadata={
            "level": event.level,
            "environment": event.environment,
            "exception_type": event.exception_type,
            # Each file holds one system's logs.
            "system": system,
            **event.metadata,
        },
        correlation_id=event.correlation_id,
    )


def _load_deployments(data_dir: Path) -> list[EvidenceItem]:
    items = []
    for path in sorted((data_dir / "deployments").glob("*.json")):
        for raw in _read_json(path):
            record = DeploymentRecord.model_validate(raw)
            items.append(
                EvidenceItem(
                    evidence_id=record.deployment_id,
                    source_type="deployment",
                    source_name=record.service,
                    timestamp=record.timestamp,
                    title=f"{record.service} {record.version} deployment",
                    content="\n".join(record.changes),
                    metadata={
                        "version": record.version,
                        "status": record.status,
                        "system": path.stem,
                    },
                )
            )
    return items


def _load_alerts(data_dir: Path) -> list[EvidenceItem]:
    items = []
    for path in sorted((data_dir / "alerts").glob("*.json")):
        for raw in _read_json(path):
            record = AlertRecord.model_validate(raw)
            items.append(
                EvidenceItem(
                    evidence_id=record.alert_id,
                    source_type="alert",
                    source_name=record.service,
                    timestamp=record.fired_at,
                    title=record.title,
                    content=record.description,
                    metadata={"severity": record.severity, "status": record.status},
                )
            )
    return items


def _load_metrics(data_dir: Path) -> list[EvidenceItem]:
    items = []
    for path in sorted((data_dir / "metrics").glob("*.json")):
        for raw in _read_json(path):
            series = MetricSeries.model_validate(raw).model_dump(mode="json")
            item = metric_evidence(**series)
            if item is not None:
                items.append(item)
    return items


def _load_dependency_maps(data_dir: Path) -> list[EvidenceItem]:
    items = []
    for path in sorted((data_dir / "dependency_maps").glob("*.json")):
        record = DependencyMapRecord.model_validate(_read_json(path))
        edges = [edge.model_dump(by_alias=True) for edge in record.edges]
        items.append(
            EvidenceItem(
                evidence_id=record.map_id,
                source_type="dependency_map",
                source_name=record.system,
                title=f"{record.system} dependency map",
                content="\n".join(f"{edge['from']} -> {edge['to']}" for edge in edges),
                metadata={
                    "nodes": [node.model_dump() for node in record.nodes],
                    "edges": edges,
                },
            )
        )
    return items


def _load_documents(data_dir: Path) -> list[EvidenceItem]:
    items = []
    for folder, source_type in DOCUMENT_FOLDERS.items():
        for path in sorted((data_dir / folder).glob("*.md")):
            fields, body = _split_front_matter(path.read_text(encoding="utf-8"))
            header = DocumentHeader.model_validate(fields)
            if header.document_type != source_type:
                raise ValueError(
                    f"{path} is a {header.document_type}, not a {source_type}"
                )
            metadata = header.model_dump(mode="json")
            metadata["source_path"] = path.relative_to(data_dir).as_posix()
            items.append(
                EvidenceItem(
                    evidence_id=header.document_id,
                    source_type=source_type,
                    source_name=header.service,
                    title=header.title,
                    content=body,
                    metadata=metadata,
                )
            )
    return items


def _split_front_matter(text: str) -> tuple[dict[str, str], str]:
    _, header, body = text.split("---", 2)
    fields: dict[str, str] = {}
    for line in header.strip().splitlines():
        key, value = line.split(": ", 1)
        fields[key] = value
    return fields, body.strip()
