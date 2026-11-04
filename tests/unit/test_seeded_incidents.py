"""Checks every seeded incident is complete and consistent with its ground truth."""

from datetime import datetime

import pytest

from flowguard.dataset import (
    incident_ids,
    load_evidence,
    load_ground_truth,
    load_incident,
)
from flowguard.domain.hypotheses import CATEGORY_DEFINITIONS
from flowguard.domain.incidents import Incident
from flowguard.domain.remediation import CATALOGUE

EVIDENCE = load_evidence()
BY_ID = {item.evidence_id: item for item in EVIDENCE}
INCIDENTS = incident_ids()


def window(incident_id: str) -> tuple[datetime, datetime]:
    incident = Incident.model_validate(load_incident(incident_id))
    return incident.start_time, incident.end_time


def logs_in_window(incident_id: str):
    start, end = window(incident_id)
    return [
        item
        for item in EVIDENCE
        if item.source_type == "log" and start <= item.timestamp <= end
    ]


def test_there_are_seeded_incidents_with_ground_truth():
    assert INCIDENTS[:3] == ["INC-001", "INC-002", "INC-003"]
    for incident_id in INCIDENTS:
        assert load_ground_truth(incident_id)["incident_id"] == incident_id


def test_evidence_ids_are_unique():
    assert len(BY_ID) == len(EVIDENCE)


def test_incident_windows_do_not_overlap():
    # Logs are searched by time alone, so overlapping windows would mix incidents.
    windows = sorted(window(incident_id) for incident_id in INCIDENTS)
    for (_, end), (next_start, _) in zip(windows, windows[1:], strict=False):
        assert end < next_start


@pytest.mark.parametrize("incident_id", INCIDENTS)
def test_ground_truth_is_complete(incident_id):
    truth = load_ground_truth(incident_id)

    assert truth["category"] in CATEGORY_DEFINITIONS
    assert truth["required_evidence_ids"]
    assert truth["reference_plan"]
    assert isinstance(truth["expected_approval_required"], bool)


@pytest.mark.parametrize("incident_id", INCIDENTS)
def test_required_evidence_exists(incident_id):
    for evidence_id in load_ground_truth(incident_id)["required_evidence_ids"]:
        assert evidence_id in BY_ID


@pytest.mark.parametrize("incident_id", INCIDENTS)
def test_the_reference_plan_uses_catalogue_actions(incident_id):
    for step in load_ground_truth(incident_id)["reference_plan"]:
        assert step["action"] in CATALOGUE


@pytest.mark.parametrize("incident_id", INCIDENTS)
def test_the_window_has_an_error_to_start_from(incident_id):
    errors = [
        item
        for item in logs_in_window(incident_id)
        if item.metadata["level"] == "ERROR"
    ]

    assert errors


@pytest.mark.parametrize("incident_id", INCIDENTS)
def test_every_logged_service_is_in_its_system_s_map(incident_id):
    system = load_incident(incident_id)["affected_system"]
    [dependency_map] = [
        item
        for item in EVIDENCE
        if item.source_type == "dependency_map" and item.source_name == system
    ]
    nodes = {node["name"] for node in dependency_map.metadata["nodes"]}
    logged = {
        item.source_name
        for item in EVIDENCE
        if item.source_type == "log" and item.metadata["system"] == system
    }

    assert logged <= nodes
