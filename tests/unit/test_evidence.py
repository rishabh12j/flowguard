from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from flowguard.domain.evidence import EvidenceItem


def log_882_fields() -> dict:
    return {
        "evidence_id": "LOG-882",
        "source_type": "log",
        "source_name": "invoice-transformer",
        "timestamp": "2026-07-15T09:43:17Z",
        "title": "SchemaValidationError",
        "content": "Payload validation failed: required field supplier_id is missing",
        "metadata": {
            "level": "ERROR",
            "environment": "demo",
            "exception_type": "SchemaValidationError",
            "source_system": "supplier-api",
            "schema_version": "3.1",
        },
        "correlation_id": "CORR-2048",
    }


def test_accepts_the_inc_001_log_event():
    item = EvidenceItem(**log_882_fields())

    assert item.evidence_id == "LOG-882"
    assert item.timestamp == datetime(2026, 7, 15, 9, 43, 17, tzinfo=timezone.utc)
    assert item.content == "Payload validation failed: required field supplier_id is missing"
    assert item.correlation_id == "CORR-2048"
    assert item.retrieval_score is None


def test_rejects_evidence_without_an_id():
    fields = log_882_fields()
    del fields["evidence_id"]

    with pytest.raises(ValidationError):
        EvidenceItem(**fields)


def test_rejects_a_blank_id():
    fields = log_882_fields()
    fields["evidence_id"] = ""

    with pytest.raises(ValidationError):
        EvidenceItem(**fields)


def test_rejects_a_whitespace_id():
    fields = log_882_fields()
    fields["evidence_id"] = "   "

    with pytest.raises(ValidationError):
        EvidenceItem(**fields)


def test_rejects_an_unknown_source_type():
    fields = log_882_fields()
    fields["source_type"] = "deployement"

    with pytest.raises(ValidationError):
        EvidenceItem(**fields)


def test_rejects_a_timestamp_without_a_timezone():
    fields = log_882_fields()
    fields["timestamp"] = "2026-07-15T09:43:17"

    with pytest.raises(ValidationError):
        EvidenceItem(**fields)


def test_rejects_a_misspelled_field():
    fields = log_882_fields()
    fields["correlation_Id"] = fields.pop("correlation_id")

    with pytest.raises(ValidationError):
        EvidenceItem(**fields)


def test_evidence_cannot_be_changed():
    item = EvidenceItem(**log_882_fields())

    with pytest.raises(ValidationError):
        item.content = "rewritten"


def test_runbook_can_have_no_timestamp_or_correlation_id():
    item = EvidenceItem(
        evidence_id="RUNBOOK-SCHEMA-01",
        source_type="runbook",
        source_name="invoice-processing",
        title="Verify schema compatibility",
        content="Verify schema compatibility after source deployments.",
        metadata={},
    )

    assert item.timestamp is None
    assert item.correlation_id is None


def test_accepts_a_score_of_zero():
    fields = log_882_fields()
    fields["retrieval_score"] = 0.0

    assert EvidenceItem(**fields).retrieval_score == 0.0


def test_rejects_a_score_above_one():
    fields = log_882_fields()
    fields["retrieval_score"] = 1.5

    with pytest.raises(ValidationError):
        EvidenceItem(**fields)


def test_rejects_a_score_below_zero():
    fields = log_882_fields()
    fields["retrieval_score"] = -0.2

    with pytest.raises(ValidationError):
        EvidenceItem(**fields)
