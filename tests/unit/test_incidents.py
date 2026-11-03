import pytest
from pydantic import ValidationError

from flowguard.dataset import load_incident
from flowguard.domain.incidents import Incident

VALID = {
    "incident_id": "INC-001",
    "description": "Invoice INV-2048 did not enter the approval workflow.",
    "affected_system": "invoice-processing",
    "start_time": "2026-07-15T09:00:00Z",
    "end_time": "2026-07-15T11:00:00Z",
}


def with_changes(**changes) -> dict:
    return {**VALID, **changes}


def test_inc_001_is_a_valid_incident():
    incident = Incident.model_validate(load_incident("INC-001"))

    assert incident.affected_system == "invoice-processing"


def test_strips_surrounding_whitespace():
    incident = Incident.model_validate(
        with_changes(incident_id=" INC-001 ", description="  Invoices failed.\n")
    )

    assert incident.incident_id == "INC-001"
    assert incident.description == "Invoices failed."


@pytest.mark.parametrize("description", ["", "   "])
def test_rejects_a_blank_description(description):
    with pytest.raises(ValidationError, match="description"):
        Incident.model_validate(with_changes(description=description))


@pytest.mark.parametrize("field", ["incident_id", "affected_system"])
def test_rejects_an_identifier_with_a_space(field):
    with pytest.raises(ValidationError, match=field):
        Incident.model_validate(with_changes(**{field: "invoice processing"}))


def test_rejects_a_time_without_a_timezone():
    with pytest.raises(ValidationError, match="start_time"):
        Incident.model_validate(with_changes(start_time="2026-07-15T09:00:00"))


@pytest.mark.parametrize("end_time", ["2026-07-15T08:00:00Z", "2026-07-15T09:00:00Z"])
def test_rejects_a_window_that_does_not_move_forward(end_time):
    with pytest.raises(ValidationError, match="end_time must be after start_time"):
        Incident.model_validate(with_changes(end_time=end_time))


def test_rejects_an_unknown_field():
    with pytest.raises(ValidationError, match="severity"):
        Incident.model_validate(with_changes(severity="high"))


def test_cannot_be_changed_after_creation():
    incident = Incident.model_validate(VALID)

    with pytest.raises(ValidationError):
        incident.affected_system = "payroll"
