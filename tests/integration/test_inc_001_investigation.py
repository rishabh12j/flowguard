import json
from contextlib import nullcontext
from functools import partial

import pytest
from fastapi.testclient import TestClient
from langgraph.checkpoint.memory import InMemorySaver

from flowguard.api.app import create_app
from flowguard.api.dependencies import Services
from flowguard.config import AUDIT_DB_VARIABLE, CHECKPOINT_DB_VARIABLE
from flowguard.dataset import load_incident
from flowguard.domain.audit import DuplicateVersion
from flowguard.graph.builder import build_graph, investigate
from flowguard.graph.checkpoints import SERIALIZER
from flowguard.graph.context import Dependencies
from flowguard.mcp.evidence_tools import open_evidence_tools
from flowguard.rag.retrieval import retrieve
from flowguard.storage.audit_repository import SqliteAuditStore

pytestmark = pytest.mark.anyio

INC_001_PLAN = [
    {
        "action": "update_field_mapping",
        "target": "invoice-transformer",
        "reason": "Map supplierId to supplier_id.",
        "evidence_ids": ["LOG-882"],
    },
    {
        "action": "replay_failed_messages",
        "target": "invoice-transformer",
        "reason": "Resend the invoices that failed.",
        "evidence_ids": ["LOG-882"],
    },
    {
        "action": "add_contract_test",
        "target": "supplier-api",
        "reason": "Catch renamed fields before deployment.",
        "evidence_ids": ["DEPLOY-SOURCE-221"],
    },
]


class ScriptedLLM:
    """Proposes INC-001's root cause, then the runbook's plan to fix it."""

    def generate(self, system: str, prompt: str, schema: dict) -> str:
        if "actions" in schema["properties"]:
            return json.dumps({"actions": INC_001_PLAN})
        hypothesis = {
            "description": "supplier-api 4.2.0 started sending camelCase fields.",
            "supporting_evidence_ids": ["LOG-882", "DEPLOY-SOURCE-221"],
            "contradicting_evidence_ids": [],
            "missing_evidence": [],
            "category": "schema_contract_mismatch",
        }
        return json.dumps({"hypotheses": [hypothesis]})


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def store():
    return SqliteAuditStore()


@pytest.fixture
async def state(client, embedder, store):
    search = partial(retrieve, embedder=embedder, client=client)
    async with open_evidence_tools(search) as tools:
        dependencies = Dependencies(tools=tools, llm=ScriptedLLM(), audit=store)
        return await investigate(
            build_graph(InMemorySaver(serde=SERIALIZER)),
            load_incident("INC-001"),
            dependencies,
        )


def evidence_ids(state) -> set[str]:
    return {item.evidence_id for item in state["evidence"]}


async def test_inc_001_runs_without_errors(state):
    assert state["errors"] == ()


async def test_inc_001_finds_its_first_failure(state):
    assert state["first_failure"].evidence_id == "LOG-882"


async def test_inc_001_gathers_every_required_kind_of_evidence(state):
    documents = {item.metadata.get("document_id") for item in state["evidence"]}

    assert {"LOG-882", "DEPLOY-SOURCE-221", "DEPMAP-INVOICE"} <= evidence_ids(state)
    assert {"RB-SCHEMA-COMPAT", "HIST-INC-044"} <= documents


async def test_inc_001_drops_the_decoy_deployments(state):
    assert "DEPLOY-WORKFLOW-118" not in evidence_ids(state)
    assert "DEPLOY-TRANSFORM-096" not in evidence_ids(state)


async def test_inc_001_scores_the_proposed_root_cause_from_real_evidence(state):
    best = state["selected_root_cause"]

    assert best.confidence == 0.75
    assert best.confidence_reason == (
        "+0.30 cites an error log; "
        "+0.20 a cited change came before the first failure; "
        "+0.15 a cited change is at or upstream of the failure; "
        "+0.10 cites a deployment"
    )


async def test_inc_001_takes_the_root_cause_s_category(state):
    assert state["category"] == "schema_contract_mismatch"


async def test_inc_001_gets_the_runbook_s_plan(state):
    assert [(action.action, action.target) for action in state["actions"]] == [
        ("update_field_mapping", "invoice-transformer"),
        ("replay_failed_messages", "invoice-transformer"),
        ("add_contract_test", "supplier-api"),
    ]
    assert state["rejected_actions"] == ()
    assert state["requires_approval"] is True


async def test_inc_001_is_saved_with_every_tool_call(state, store):
    record = store.get(state["investigation_id"])

    assert record.status == "awaiting_approval"
    # Logs and documents are searched in parallel, so the order can vary.
    assert sorted((call.tool, call.outcome) for call in record.tool_calls) == [
        ("get_dependency_map", "ok"),
        ("get_deployments", "ok"),
        # Once for each service at or upstream of invoice-transformer.
        ("get_metrics", "ok"),
        ("get_metrics", "ok"),
        ("get_metrics", "ok"),
        ("search_alerts", "ok"),
        ("search_logs", "ok"),
        ("search_runbooks", "ok"),
    ]
    assert any(item.startswith("SPEC-INVOICE-V3") for item in record.evidence_ids)
    assert "LOG-882" in record.evidence_ids


def services_for(client, embedder, store=None) -> Services:
    return Services(
        graph=build_graph(InMemorySaver(serde=SERIALIZER)),
        llm=ScriptedLLM(),
        audit=store or SqliteAuditStore(),
        open_tools=partial(
            open_evidence_tools, partial(retrieve, embedder=embedder, client=client)
        ),
    )


def test_inc_001_is_diagnosed_through_the_api(client, embedder):
    services = services_for(client, embedder)

    with TestClient(create_app(lambda: nullcontext(services))) as api:
        first = api.post("/investigations", json=load_incident("INC-001"))
        second = api.post("/investigations", json=load_incident("INC-001"))

    assert first.status_code == 201
    assert first.json()["status"] == "awaiting_approval"
    assert first.json()["category"] == "schema_contract_mismatch"

    # Each investigation has its own tool guard and history.
    def calls(response):
        return [
            (call["tool"], call["outcome"]) for call in response.json()["tool_calls"]
        ]

    assert calls(second) == calls(first)


def test_the_api_starts_with_the_real_services(monkeypatch, tmp_path):
    monkeypatch.setenv(AUDIT_DB_VARIABLE, str(tmp_path / "audit.db"))
    monkeypatch.setenv(CHECKPOINT_DB_VARIABLE, str(tmp_path / "checkpoints.db"))

    with TestClient(create_app()) as api:
        response = api.get("/health")

    assert response.status_code == 200
    assert (tmp_path / "audit.db").exists()
    assert (tmp_path / "checkpoints.db").exists()


@pytest.fixture
def paused_api(client, embedder):
    with TestClient(
        create_app(lambda: nullcontext(services_for(client, embedder)))
    ) as api:
        started = api.post("/investigations", json=load_incident("INC-001")).json()
        yield api, f"/investigations/{started['investigation_id']}"


def test_an_approval_through_the_api_is_recorded(paused_api):
    api, path = paused_api

    response = api.post(f"{path}/approve", json={"approver": "sam"})

    assert response.status_code == 200
    assert response.json()["status"] == "approved"
    assert response.json()["decision"]["approver"] == "sam"
    events = api.get(f"{path}/events").json()
    assert [(event["version"], event["status"]) for event in events] == [
        (1, "awaiting_approval"),
        (2, "approved"),
    ]


def test_an_investigation_cannot_be_decided_twice(paused_api):
    api, path = paused_api
    api.post(f"{path}/approve", json={"approver": "sam"})

    response = api.post(f"{path}/reject", json={"approver": "alex", "comment": "No."})

    assert response.status_code == 409
    assert api.get(path).json()["status"] == "approved"


def test_a_rejection_needs_a_comment(paused_api):
    api, path = paused_api

    response = api.post(f"{path}/reject", json={"approver": "sam"})

    assert response.status_code == 422
    assert response.json() == {
        "detail": ["request: Value error, reject needs a comment saying why"]
    }
    assert api.get(path).json()["status"] == "awaiting_approval"


def test_a_request_for_more_evidence_is_recorded(paused_api):
    api, path = paused_api

    response = api.post(
        f"{path}/request-more-evidence",
        json={"approver": "sam", "comment": "Check the ERP connector's logs too."},
    )

    # The investigation reasoned again with the request and paused for approval.
    assert response.json()["status"] == "awaiting_approval"
    assert response.json()["evidence_round"] == 1
    assert response.json()["reviewer_request"] == "Check the ERP connector's logs too."
    assert [event["status"] for event in api.get(f"{path}/events").json()] == [
        "awaiting_approval",
        "more_evidence_requested",
        "awaiting_approval",
    ]


class RacedStore(SqliteAuditStore):
    """Behaves as if another decision saved version 2 a moment earlier."""

    def save(self, record) -> None:
        if record.version == 2:
            raise DuplicateVersion(
                f"{record.investigation_id} version 2 is already saved"
            )
        super().save(record)


def test_a_decision_that_loses_a_race_is_a_conflict(client, embedder):
    services = services_for(client, embedder, RacedStore())

    with TestClient(create_app(lambda: nullcontext(services))) as api:
        started = api.post("/investigations", json=load_incident("INC-001")).json()
        path = f"/investigations/{started['investigation_id']}"
        response = api.post(f"{path}/approve", json={"approver": "sam"})

    assert response.status_code == 409
    assert response.json() == {"detail": "another decision was recorded first"}
