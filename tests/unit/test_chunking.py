import pytest

from flowguard.dataset import load_evidence
from flowguard.rag.chunking import chunk_document

EVIDENCE = {item.evidence_id: item for item in load_evidence()}
SPEC = EVIDENCE["SPEC-INVOICE-V3"]
RUNBOOK = EVIDENCE["RB-SCHEMA-COMPAT"]
HISTORICAL = EVIDENCE["HIST-INC-044"]
ALL_CHUNKS = [
    chunk for item in (SPEC, RUNBOOK, HISTORICAL) for chunk in chunk_document(item)
]


def test_runbook_keeps_steps_with_their_warnings():
    chunks = chunk_document(RUNBOOK)

    assert len(chunks) == 1
    assert "## Prerequisites" in chunks[0].text
    assert "## Procedure" in chunks[0].text
    assert "## Warnings" in chunks[0].text


def test_historical_incident_keeps_symptoms_with_the_resolution():
    chunks = chunk_document(HISTORICAL)

    assert len(chunks) == 1
    assert "## Symptoms" in chunks[0].text
    assert "## Root cause" in chunks[0].text
    assert "## Resolution" in chunks[0].text


def test_spec_splits_into_an_overview_and_each_operation():
    chunks = chunk_document(SPEC)

    assert [chunk.section for chunk in chunks] == ["Overview", "POST /v3/invoices"]


def test_spec_keeps_an_operation_together():
    operation = chunk_document(SPEC)[1].text

    assert operation.startswith("## POST /v3/invoices")
    assert "### Headers" in operation
    assert "### Request body" in operation
    assert "### Validation failure" in operation
    assert "SchemaValidationError" in operation


def test_a_spec_with_several_operations_keeps_each_one_whole():
    content = "## GET /a\n\nFirst.\n\n### Notes\n\nA note.\n\n## GET /b\n\nSecond."
    item = SPEC.model_copy(update={"content": content})

    chunks = chunk_document(item)

    assert [chunk.section for chunk in chunks] == ["GET /a", "GET /b"]
    assert chunks[0].text == "## GET /a\n\nFirst.\n\n### Notes\n\nA note."
    assert chunks[1].text == "## GET /b\n\nSecond."


def test_a_spec_without_sections_is_one_chunk():
    item = SPEC.model_copy(update={"content": "Just a paragraph."})

    chunks = chunk_document(item)

    assert [chunk.text for chunk in chunks] == ["Just a paragraph."]


def test_chunk_text_is_copied_exactly():
    for item in (SPEC, RUNBOOK, HISTORICAL):
        assert all(chunk.text in item.content for chunk in chunk_document(item))


def test_no_text_is_lost():
    spec_text = "\n".join(chunk.text for chunk in chunk_document(SPEC))

    for line in SPEC.content.splitlines():
        assert line in spec_text


def test_chunk_ids_are_readable_and_unique():
    ids = [chunk.chunk_id for chunk in ALL_CHUNKS]

    assert "SPEC-INVOICE-V3#post-v3-invoices" in ids
    assert len(ids) == len(set(ids))


def test_chunk_ids_stay_the_same_between_runs():
    assert chunk_document(SPEC) == chunk_document(SPEC)


def test_chunks_carry_their_source_metadata():
    chunk = chunk_document(SPEC)[1]

    assert chunk.document_id == "SPEC-INVOICE-V3"
    assert chunk.document_type == "api_spec"
    assert chunk.title == "Invoice ingestion contract"
    assert chunk.system == "invoice-processing"
    assert chunk.service == "invoice-transformer"
    assert chunk.version == "3.1"
    assert chunk.effective_date == "2026-06-02"
    assert chunk.source_path == "api_specs/SPEC-INVOICE-V3.md"


def test_chunks_keep_a_superseded_document_marked():
    metadata = {**RUNBOOK.metadata, "is_current": False}
    item = RUNBOOK.model_copy(update={"metadata": metadata})

    assert chunk_document(item)[0].is_current is False


def test_rejects_evidence_that_is_not_a_document():
    with pytest.raises(ValueError, match="LOG-882"):
        chunk_document(EVIDENCE["LOG-882"])
