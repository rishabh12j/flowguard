from contextlib import asynccontextmanager, nullcontext

import pytest
from fakes import FakeLLM
from fastapi.testclient import TestClient
from langgraph.checkpoint.memory import InMemorySaver

from flowguard.api.app import create_app
from flowguard.api.dependencies import Services
from flowguard.domain.audit import ToolCallRecord
from flowguard.graph.builder import build_graph
from flowguard.graph.checkpoints import SERIALIZER
from flowguard.graph.context import Found
from flowguard.storage.audit_repository import SqliteAuditStore

REQUEST = {
    "incident_id": "INC-001",
    "description": "Invoice INV-2048 did not enter the approval workflow.",
    "affected_system": "invoice-processing",
    "start_time": "2026-07-15T09:00:00Z",
    "end_time": "2026-07-15T11:00:00Z",
}


class EmptyTools:
    """Finds nothing, but records each call like the real tools do."""

    def __init__(self) -> None:
        self.history: list[ToolCallRecord] = []

    def _record(self, tool: str) -> Found:
        self.history.append(
            ToolCallRecord(tool=tool, arguments={}, outcome="ok", seconds=0)
        )
        return Found([])

    async def search_logs(self, start_time, end_time) -> Found:
        return self._record("search_logs")

    async def get_deployments(self, start_time, end_time) -> Found:
        return self._record("get_deployments")

    async def get_dependency_map(self, service) -> Found:
        return self._record("get_dependency_map")

    async def search_runbooks(self, query, system) -> Found:
        return self._record("search_runbooks")

    async def search_alerts(self, start_time, end_time) -> Found:
        return self._record("search_alerts")

    async def get_metrics(self, service, start_time, end_time) -> Found:
        return self._record("get_metrics")


class Toolbox:
    """Opens new tools for each investigation, and keeps every set it opened."""

    def __init__(self) -> None:
        self.opened: list[EmptyTools] = []

    @asynccontextmanager
    async def open(self):
        tools = EmptyTools()
        self.opened.append(tools)
        yield tools


class BrokenStore(SqliteAuditStore):
    def save(self, record) -> None:
        raise OSError(r"disk full at C:\audit\flowguard-audit.db")


def serve(store, toolbox=None, **options) -> TestClient:
    services = Services(
        graph=build_graph(InMemorySaver(serde=SERIALIZER)),
        llm=FakeLLM(),
        audit=store,
        open_tools=(toolbox or Toolbox()).open,
    )
    return TestClient(create_app(lambda: nullcontext(services)), **options)


@pytest.fixture
def store():
    return SqliteAuditStore()


@pytest.fixture
def toolbox():
    return Toolbox()


@pytest.fixture
def api(store, toolbox):
    # Using the client in a with block runs the app's startup.
    with serve(store, toolbox) as client:
        yield client


def test_health(api):
    response = api.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_starting_an_investigation_returns_its_saved_record(api, store):
    response = api.post("/investigations", json=REQUEST)

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "abstained"
    assert body["incident"]["incident_id"] == "INC-001"
    assert body == store.get(body["investigation_id"]).model_dump(mode="json")
    assert response.headers["location"] == f"/investigations/{body['investigation_id']}"


def test_an_investigation_can_be_read_back(api):
    started = api.post("/investigations", json=REQUEST)

    response = api.get(started.headers["location"])

    assert response.status_code == 200
    assert response.json() == started.json()


def test_an_unknown_investigation_is_not_found(api):
    response = api.get("/investigations/INVEST-404")

    assert response.status_code == 404
    assert response.json() == {"detail": "investigation not found"}


def test_a_rejected_request_is_saved_but_not_repeated(api, store):
    response = api.post(
        "/investigations", json={**REQUEST, "affected_system": "password hunter2"}
    )

    assert response.status_code == 422
    record = response.json()["detail"]
    assert record["status"] == "rejected"
    assert store.get(record["investigation_id"]) is not None
    assert "hunter2" not in response.text


def test_a_body_that_is_not_an_object_is_not_repeated(api):
    response = api.post("/investigations", json=["password hunter2"])

    assert response.status_code == 422
    assert response.json() == {"detail": ["body: Input should be a valid dictionary"]}


def test_each_investigation_opens_its_own_tools(api, toolbox):
    first = api.post("/investigations", json=REQUEST).json()
    second = api.post("/investigations", json=REQUEST).json()

    assert len(toolbox.opened) == 2
    assert first["tool_calls"]
    assert second["tool_calls"] == first["tool_calls"]


def test_an_audit_failure_is_an_error_that_reveals_nothing():
    with serve(BrokenStore(), raise_server_exceptions=False) as client:
        response = client.post("/investigations", json=REQUEST)

    assert response.status_code == 500
    assert "disk full" not in response.text


def test_events_list_every_saved_version(api):
    started = api.post("/investigations", json=REQUEST).json()

    response = api.get(f"/investigations/{started['investigation_id']}/events")

    assert response.status_code == 200
    assert response.json() == [started]


def test_events_of_an_unknown_investigation_are_not_found(api):
    assert api.get("/investigations/INVEST-404/events").status_code == 404


@pytest.mark.parametrize("route", ["approve", "reject", "request-more-evidence"])
def test_only_a_paused_investigation_can_be_decided(api, store, route):
    started = api.post("/investigations", json=REQUEST).json()

    response = api.post(
        f"/investigations/{started['investigation_id']}/{route}",
        json={"approver": "sam", "comment": "Looks right."},
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "the investigation is abstained, not awaiting approval"
    }
    assert len(store.history(started["investigation_id"])) == 1


def test_deciding_an_unknown_investigation_is_not_found(api):
    response = api.post("/investigations/INVEST-404/approve", json={"approver": "sam"})

    assert response.status_code == 404


def test_a_decision_needs_an_approver(api):
    response = api.post("/investigations/INVEST-404/approve", json={})

    assert response.status_code == 422
    assert response.json() == {"detail": ["body.approver: Field required"]}
