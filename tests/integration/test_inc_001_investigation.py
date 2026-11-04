from functools import partial

import pytest

from flowguard.dataset import load_incident
from flowguard.graph.builder import investigate
from flowguard.graph.context import Dependencies
from flowguard.mcp.evidence_tools import open_evidence_tools
from flowguard.rag.retrieval import retrieve

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def state(client, embedder):
    retriever = partial(retrieve, embedder=embedder, client=client)
    async with open_evidence_tools() as tools:
        dependencies = Dependencies(retriever=retriever, tools=tools)
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
