import json
from datetime import datetime

from flowguard.dataset import DATA_DIR, load_evidence, load_incident

EVIDENCE = load_evidence()
BY_ID = {item.evidence_id: item for item in EVIDENCE}
LOGS = [item for item in EVIDENCE if item.source_type == "log"]
INCIDENT = load_incident("INC-001")
GROUND_TRUTH = json.loads(
    (DATA_DIR / "ground_truth" / "INC-001.json").read_text(encoding="utf-8")
)


def logs_for(correlation_id: str) -> list:
    return [item for item in LOGS if item.correlation_id == correlation_id]


def test_evidence_ids_are_unique():
    assert len(BY_ID) == len(EVIDENCE)


def test_every_log_has_a_timestamp_and_correlation_id():
    assert all(item.timestamp and item.correlation_id for item in LOGS)


def test_every_deployment_has_a_timestamp():
    assert all(item.timestamp for item in EVIDENCE if item.source_type == "deployment")


def test_required_evidence_exists():
    assert set(GROUND_TRUTH["required_evidence_ids"]) <= set(BY_ID)


def test_log_882_matches_the_brief():
    item = BY_ID["LOG-882"]

    assert item.source_name == "invoice-transformer"
    assert item.correlation_id == "CORR-2048"
    assert (
        item.content
        == "Payload validation failed: required field supplier_id is missing"
    )
    assert item.metadata["exception_type"] == "SchemaValidationError"


def test_log_882_is_the_first_failure():
    errors = [item for item in LOGS if item.metadata["level"] == "ERROR"]

    assert min(errors, key=lambda item: item.timestamp).evidence_id == "LOG-882"


def test_source_deployment_happens_before_the_incident_window():
    start_time = datetime.fromisoformat(INCIDENT["start_time"])

    assert BY_ID["DEPLOY-SOURCE-221"].timestamp < start_time


def test_failed_transaction_never_reaches_the_workflow():
    services = {item.source_name for item in logs_for("CORR-2048")}

    assert services == {"supplier-api", "invoice-transformer"}


def test_other_source_still_succeeds_during_the_incident():
    logs = logs_for("CORR-2051")

    assert "invoice-workflow" in {item.source_name for item in logs}
    assert "ERROR" not in {item.metadata["level"] for item in logs}


def test_received_fields_changed_after_the_deployment():
    assert BY_ID["LOG-861"].metadata["received_fields"] == [
        "supplier_id",
        "total_amount",
    ]
    assert BY_ID["LOG-881"].metadata["received_fields"] == [
        "supplierId",
        "invoiceTotal",
    ]


def test_spec_requires_the_fields_missing_from_the_failed_payload():
    spec = BY_ID["SPEC-INVOICE-V3"].content

    assert "`supplier_id`" in spec
    assert "`total_amount`" in spec
    assert "supplierId" not in spec


def test_every_logged_service_is_in_the_dependency_map():
    nodes = {node["name"] for node in BY_ID["DEPMAP-INVOICE"].metadata["nodes"]}

    assert {item.source_name for item in LOGS} <= nodes


def test_documents_are_marked_current():
    documents = ("SPEC-INVOICE-V3", "RB-SCHEMA-COMPAT", "HIST-INC-044")

    assert all(
        BY_ID[document_id].metadata["is_current"] is True for document_id in documents
    )


def test_incident_report_does_not_reveal_the_root_cause():
    description = INCIDENT["description"].lower()

    assert not {"camelcase", "schema", "deploy", "mapping"} & set(
        description.replace(".", "").split()
    )
