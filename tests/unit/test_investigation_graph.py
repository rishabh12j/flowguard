from datetime import UTC, datetime, timedelta

import pytest

from flowguard.domain.evidence import EvidenceItem
from flowguard.graph.builder import GRAPH, investigate
from flowguard.graph.context import Dependencies, EvidenceUnavailable, Found

pytestmark = pytest.mark.anyio

REQUEST = {
    "incident_id": "INC-001",
    "description": "Invoice INV-2048 did not enter the approval workflow.",
    "affected_system": "invoice-processing",
    "start_time": "2026-07-15T09:00:00Z",
    "end_time": "2026-07-15T11:00:00Z",
}
WINDOW_START = datetime(2026, 7, 15, 9, tzinfo=UTC)


@pytest.fixture
def anyio_backend():
    return "asyncio"


def document(evidence_id: str) -> EvidenceItem:
    return EvidenceItem(
        evidence_id=evidence_id,
        source_type="runbook",
        source_name="invoice-transformer",
        title="A runbook",
        content="Some steps.",
        metadata={},
        retrieval_score=0.7,
    )


def log(evidence_id: str, minute: int, level: str, service: str) -> EvidenceItem:
    return EvidenceItem(
        evidence_id=evidence_id,
        source_type="log",
        source_name=service,
        timestamp=WINDOW_START + timedelta(minutes=minute),
        title=f"{level} from {service}",
        content="A log message.",
        metadata={"level": level},
    )


def deployment(evidence_id: str, at: datetime, service: str) -> EvidenceItem:
    return EvidenceItem(
        evidence_id=evidence_id,
        source_type="deployment",
        source_name=service,
        timestamp=at,
        title=f"{service} deployment",
        content="Deployed.",
        metadata={},
    )


DEPENDENCY_MAP = EvidenceItem(
    evidence_id="DEPMAP-INVOICE",
    source_type="dependency_map",
    source_name="invoice-processing",
    title="invoice-processing dependency map",
    content="supplier-api -> invoice-transformer -> invoice-workflow",
    metadata={
        "edges": [
            {"from": "supplier-api", "to": "invoice-transformer"},
            {"from": "invoice-transformer", "to": "invoice-workflow"},
        ]
    },
)
FAILURE = log("LOG-882", 43, "ERROR", "invoice-transformer")
UPSTREAM_DEPLOY = deployment(
    "DEPLOY-SOURCE-221", datetime(2026, 7, 15, 8, 5, tzinfo=UTC), "supplier-api"
)
DOWNSTREAM_DEPLOY = deployment(
    "DEPLOY-WORKFLOW-118", datetime(2026, 7, 14, 16, 20, tzinfo=UTC), "invoice-workflow"
)


class FakeRetriever:
    """Returns fixed documents and records every search."""

    def __init__(self, *documents: EvidenceItem) -> None:
        self.documents = list(documents)
        self.calls: list[tuple[str, str]] = []

    def __call__(self, query: str, *, system: str) -> list[EvidenceItem]:
        self.calls.append((query, system))
        return self.documents


class FakeTools:
    """Returns fixed evidence from each tool, and records every call."""

    def __init__(
        self,
        logs: tuple[EvidenceItem, ...] = (),
        deployments: tuple[EvidenceItem, ...] = (),
        maps: tuple[EvidenceItem, ...] = (),
        *,
        truncated: bool = False,
        failing: str | None = None,
    ) -> None:
        self.results = {
            "search_logs": Found(list(logs), truncated),
            "get_deployments": Found(list(deployments)),
            "get_dependency_map": Found(list(maps)),
        }
        self.failing = failing
        self.calls: list[tuple] = []

    def _answer(self, name: str, *arguments) -> Found:
        self.calls.append((name, *arguments))
        if name == self.failing:
            raise EvidenceUnavailable(f"{name}: timed out")
        return self.results[name]

    async def search_logs(self, start_time, end_time) -> Found:
        return self._answer("search_logs", start_time, end_time)

    async def get_deployments(self, start_time, end_time) -> Found:
        return self._answer("get_deployments", start_time, end_time)

    async def get_dependency_map(self, service) -> Found:
        return self._answer("get_dependency_map", service)


def ids(state) -> set[str]:
    # EvidenceItem can't go in a set: its metadata is a dict, which can't be hashed.
    return {item.evidence_id for item in state["evidence"]}


def called(tools: FakeTools, name: str) -> list[tuple]:
    return [call[1:] for call in tools.calls if call[0] == name]


async def run(request=REQUEST, retriever=None, tools=None):
    dependencies = Dependencies(
        retriever=retriever or FakeRetriever(), tools=tools or FakeTools()
    )
    return await investigate(request, dependencies)


async def test_a_valid_request_becomes_an_incident():
    state = await run()

    assert state["incident"].incident_id == "INC-001"
    assert state["errors"] == ()


async def test_retrieval_searches_the_description_within_the_affected_system():
    retriever = FakeRetriever()

    await run(retriever=retriever)

    assert retriever.calls == [(REQUEST["description"], "invoice-processing")]


async def test_logs_documents_maps_and_deployments_all_become_evidence():
    runbook = document("RB-SCHEMA-COMPAT#full-document")
    tools = FakeTools((FAILURE,), (UPSTREAM_DEPLOY,), (DEPENDENCY_MAP,))

    state = await run(retriever=FakeRetriever(runbook), tools=tools)

    assert ids(state) == {
        "RB-SCHEMA-COMPAT#full-document",
        "LOG-882",
        "DEPMAP-INVOICE",
        "DEPLOY-SOURCE-221",
    }


async def test_logs_are_searched_in_the_incident_window():
    tools = FakeTools()

    await run(tools=tools)

    assert called(tools, "search_logs") == [
        (WINDOW_START, datetime(2026, 7, 15, 11, tzinfo=UTC))
    ]


async def test_the_first_failure_is_the_earliest_error():
    later = log("LOG-886", 48, "ERROR", "invoice-transformer")
    warning = log("LOG-801", 1, "WARN", "invoice-workflow")
    tools = FakeTools((later, warning, FAILURE))

    state = await run(tools=tools)

    assert state["first_failure"] == FAILURE


async def test_deployments_are_searched_in_the_day_before_the_first_failure():
    tools = FakeTools((FAILURE,))

    await run(tools=tools)

    failed_at = FAILURE.timestamp
    assert called(tools, "get_deployments") == [
        (failed_at - timedelta(hours=24), failed_at)
    ]
    assert called(tools, "get_dependency_map") == [("invoice-transformer",)]


async def test_deployments_downstream_of_the_failure_are_dropped():
    tools = FakeTools(
        (FAILURE,), (UPSTREAM_DEPLOY, DOWNSTREAM_DEPLOY), (DEPENDENCY_MAP,)
    )

    state = await run(tools=tools)

    assert UPSTREAM_DEPLOY in state["evidence"]
    assert DOWNSTREAM_DEPLOY not in state["evidence"]


async def test_without_a_map_every_deployment_is_kept():
    tools = FakeTools((FAILURE,), (UPSTREAM_DEPLOY, DOWNSTREAM_DEPLOY))

    state = await run(tools=tools)

    assert {"DEPLOY-SOURCE-221", "DEPLOY-WORKFLOW-118"} <= ids(state)


async def test_without_an_error_deployments_are_searched_before_the_window():
    tools = FakeTools((log("LOG-801", 1, "WARN", "invoice-workflow"),))

    state = await run(tools=tools)

    assert "first_failure" not in state
    assert called(tools, "get_deployments") == [
        (WINDOW_START - timedelta(hours=24), WINDOW_START)
    ]
    assert called(tools, "get_dependency_map") == []


async def test_a_failing_tool_is_recorded_and_the_investigation_continues():
    runbook = document("RB-SCHEMA-COMPAT#full-document")
    tools = FakeTools((FAILURE,), failing="search_logs")

    state = await run(retriever=FakeRetriever(runbook), tools=tools)

    assert state["errors"] == ("log_analysis: search_logs: timed out",)
    assert runbook in state["evidence"]
    assert called(tools, "get_deployments")


async def test_a_failing_dependency_tool_keeps_the_logs():
    tools = FakeTools((FAILURE,), failing="get_deployments")

    state = await run(tools=tools)

    assert state["errors"] == ("dependency_trace: get_deployments: timed out",)
    assert FAILURE in state["evidence"]


async def test_truncated_logs_are_reported():
    state = await run(tools=FakeTools((FAILURE,), truncated=True))

    assert state["errors"] == ("log_analysis: only the earliest logs were returned",)


async def test_an_invalid_request_calls_no_tools():
    retriever = FakeRetriever(document("RB-SCHEMA-COMPAT#full-document"))
    tools = FakeTools((FAILURE,))

    state = await run({**REQUEST, "end_time": "2026-07-15T08:00:00Z"}, retriever, tools)

    assert "incident" not in state
    assert state["evidence"] == ()
    assert retriever.calls == []
    assert tools.calls == []


async def test_errors_name_each_problem():
    request = {key: value for key, value in REQUEST.items() if key != "description"}

    state = await run({**request, "start_time": "2026-07-15T09:00:00"})

    assert state["errors"] == (
        "description: Field required",
        "start_time: Input should have timezone info",
    )


async def test_errors_do_not_repeat_the_rejected_value():
    state = await run({**REQUEST, "affected_system": "password hunter2"})

    assert state["errors"]
    assert not any("hunter2" in error for error in state["errors"])


async def test_a_missing_request_is_rejected():
    dependencies = Dependencies(retriever=FakeRetriever(), tools=FakeTools())

    state = await GRAPH.ainvoke({}, context=dependencies)

    assert "incident_id: Field required" in state["errors"]


async def test_evidence_already_in_the_state_is_kept():
    earlier = document("NOTE-1")
    runbook = document("RB-SCHEMA-COMPAT#full-document")
    dependencies = Dependencies(retriever=FakeRetriever(runbook), tools=FakeTools())

    state = await GRAPH.ainvoke(
        {"request": REQUEST, "evidence": (earlier,)}, context=dependencies
    )

    assert earlier in state["evidence"]
    assert runbook in state["evidence"]
