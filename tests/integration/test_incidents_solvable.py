"""Proves each seeded incident can be solved by the real graph from its evidence.

An oracle stands in for the model: it cites the ground truth's evidence and
proposes the ground truth's plan. Everything else is real: the MCP servers, the
retrieval, the scoring, and the validation. If an incident can't be solved even
with perfect answers, its data is incomplete.
"""

import json
from functools import partial

import pytest
from langgraph.checkpoint.memory import InMemorySaver

from flowguard.dataset import incident_ids, load_ground_truth, load_incident
from flowguard.graph.builder import build_graph, investigate
from flowguard.graph.checkpoints import SERIALIZER
from flowguard.graph.context import Dependencies
from flowguard.graph.nodes.root_cause import MIN_CONFIDENCE
from flowguard.mcp.evidence_tools import open_evidence_tools
from flowguard.rag.retrieval import retrieve
from flowguard.seed_schemas import GroundTruth
from flowguard.storage.audit_repository import SqliteAuditStore

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


def offered(schema: dict, model: str, field: str) -> list[str]:
    """The evidence IDs the schema lets the model cite."""
    properties = schema["$defs"][model]["properties"]
    return properties[field]["items"]["enum"]


class Oracle:
    """Answers as if it knew the ground truth, citing only evidence it was given."""

    def __init__(self, truth: GroundTruth) -> None:
        self.truth = truth
        self.required = set(truth.required_evidence_ids)

    def cited(self, available: list[str]) -> list[str]:
        # Documents are cited by chunk, so SPEC-X#section matches SPEC-X.
        return [item for item in available if item.split("#")[0] in self.required]

    def generate(self, system: str, prompt: str, schema: dict) -> str:
        if "actions" in schema["properties"]:
            cited = self.cited(offered(schema, "ProposedAction", "evidence_ids"))
            steps = [
                {
                    **step.model_dump(),
                    "reason": "From the runbook.",
                    "evidence_ids": cited[:1],
                }
                for step in self.truth.reference_plan
            ]
            return json.dumps({"actions": steps})
        cited = self.cited(
            offered(schema, "ProposedHypothesis", "supporting_evidence_ids")
        )
        hypothesis = {
            "description": self.truth.root_cause,
            "category": self.truth.category,
            "supporting_evidence_ids": cited,
            "contradicting_evidence_ids": [],
            "missing_evidence": [],
        }
        return json.dumps({"hypotheses": [hypothesis]})


@pytest.fixture(params=incident_ids())
async def solved(request, client, embedder):
    truth = load_ground_truth(request.param)
    search = partial(retrieve, embedder=embedder, client=client)
    async with open_evidence_tools(search) as tools:
        dependencies = Dependencies(
            tools=tools, llm=Oracle(truth), audit=SqliteAuditStore()
        )
        state = await investigate(
            build_graph(InMemorySaver(serde=SERIALIZER)),
            load_incident(request.param),
            dependencies,
        )
    return truth, state


async def test_the_required_evidence_is_gathered(solved):
    truth, state = solved

    gathered = {item.evidence_id.split("#")[0] for item in state["evidence"]}
    assert set(truth.required_evidence_ids) <= gathered


async def test_the_ground_truth_root_cause_is_selected(solved):
    truth, state = solved

    assert state["errors"] == ()
    assert state["category"] == truth.category
    assert state["selected_root_cause"].confidence >= MIN_CONFIDENCE


async def test_the_reference_plan_passes_validation(solved):
    truth, state = solved

    planned = [{"action": a.action, "target": a.target} for a in state["actions"]]
    assert planned == [step.model_dump() for step in truth.reference_plan]
    assert state["rejected_actions"] == ()
    assert state["requires_approval"] is truth.expected_approval_required
