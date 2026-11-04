import json

import pytest
from pydantic import ValidationError

from flowguard.dataset import DATA_DIR, load_evidence
from flowguard.seed_schemas import (
    DependencyMapRecord,
    GroundTruth,
    LogRecord,
    MetricSeries,
)

LOG = {
    "event_id": "LOG-1",
    "timestamp": "2026-08-17T09:00:02Z",
    "service": "bank-ack-poller",
    "environment": "demo",
    "level": "ERROR",
    "correlation_id": "CORR-1",
    "message": "No acknowledgement within 2 hours.",
    "exception_type": "AckTimeout",
    "metadata": {},
}


def test_a_valid_log_record_is_accepted():
    assert LogRecord.model_validate(LOG).level == "ERROR"


@pytest.mark.parametrize(
    "change",
    [
        {"level": "FATAL"},
        {"timestamp": "2026-08-17T09:00:02"},
        {"event_id": "LOG 1"},
        {"message": ""},
        {"unexpected": True},
    ],
)
def test_a_bad_log_record_is_refused(change):
    with pytest.raises(ValidationError):
        LogRecord.model_validate({**LOG, **change})


def test_a_map_edge_must_join_known_nodes():
    with pytest.raises(ValidationError, match="unknown nodes: \\['bank-sftp'\\]"):
        DependencyMapRecord.model_validate(
            {
                "map_id": "DEPMAP-1",
                "system": "vendor-payments",
                "nodes": [{"name": "sftp-uploader", "type": "job"}],
                "edges": [{"from": "sftp-uploader", "to": "bank-sftp"}],
            }
        )


def test_metric_points_must_be_in_time_order():
    with pytest.raises(ValidationError, match="time order"):
        MetricSeries.model_validate(
            {
                "series_id": "METRIC-1",
                "service": "account-api",
                "metric": "requests_per_minute",
                "unit": "requests/min",
                "threshold": 3000,
                "points": [
                    {"timestamp": "2026-08-24T08:10:00Z", "value": 1},
                    {"timestamp": "2026-08-24T08:00:00Z", "value": 2},
                ],
            }
        )


def test_ground_truth_needs_a_known_category():
    truth = json.loads((DATA_DIR / "ground_truth" / "INC-001.json").read_text())

    with pytest.raises(ValidationError):
        GroundTruth.model_validate({**truth, "category": "gremlins"})


def test_a_document_in_the_wrong_folder_is_refused(tmp_path):
    for folder in ("logs", "deployments", "alerts", "metrics", "dependency_maps"):
        (tmp_path / folder).mkdir()
    (tmp_path / "runbooks").mkdir()
    (tmp_path / "runbooks" / "RB-1.md").write_text(
        "---\ndocument_id: RB-1\ndocument_type: api_spec\ntitle: A spec\n"
        "system: s\nservice: s\nversion: 1\neffective_date: 2026-01-01\n"
        "is_current: true\n---\n\nBody.",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="is a api_spec, not a runbook"):
        load_evidence(tmp_path)
