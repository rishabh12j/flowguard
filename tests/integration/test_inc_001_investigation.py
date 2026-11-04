import json
from functools import partial

import pytest

from flowguard.dataset import load_incident
from flowguard.graph.builder import investigate
from flowguard.graph.context import Dependencies
from flowguard.mcp.evidence_tools import open_evidence_tools
from flowguard.rag.retrieval import retrieve
from flowguard.storage.audit_repository import SqliteAuditStore

pytestmark = pytest.mark.anyio


class ScriptedLLM:
    """Always proposes INC-001's root cause, citing a failing log and a deployment."""

    def generate(self, system: str, prompt: str, schema: dict) -> str:
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
    retriever = partial(retrieve, embedder=embedder, client=client)
    async with open_evidence_tools() as tools:
        dependencies = Dependencies(
            retriever=retriever, tools=tools, llm=ScriptedLLM(), audit=store
        )
        return await investigate(load_incident("INC-001"), dependencies)


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
        "+0.20 a cited deployment came before the first failure; "
        "+0.15 a cited deployment is upstream of the failure; "
        "+0.10 cites a deployment"
    )


async def test_inc_001_takes_the_root_cause_s_category(state):
    assert state["category"] == "schema_contract_mismatch"


async def test_inc_001_is_saved_with_every_tool_call(state, store):
    record = store.get(state["investigation_id"])

    assert record.status == "diagnosed"
    assert [(call.tool, call.outcome) for call in record.tool_calls] == [
        ("search_logs", "ok"),
        ("get_deployments", "ok"),
        ("get_dependency_map", "ok"),
    ]
    assert "LOG-882" in record.evidence_ids
