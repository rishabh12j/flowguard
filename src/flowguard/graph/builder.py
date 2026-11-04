from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from flowguard.graph.context import Dependencies
from flowguard.graph.nodes.audit import audit
from flowguard.graph.nodes.dependency_trace import dependency_trace
from flowguard.graph.nodes.intake import intake
from flowguard.graph.nodes.log_analysis import log_analysis
from flowguard.graph.nodes.retrieval import runbook_retrieval
from flowguard.graph.nodes.root_cause import root_cause
from flowguard.graph.routing import after_intake
from flowguard.graph.state import InvestigationState

InvestigationGraph = CompiledStateGraph[
    InvestigationState, Dependencies, InvestigationState, InvestigationState
]


def build_graph() -> InvestigationGraph:
    graph = StateGraph(InvestigationState, context_schema=Dependencies)
    graph.add_node("intake", intake)
    graph.add_node("log_analysis", log_analysis)
    graph.add_node("dependency_trace", dependency_trace)
    graph.add_node("runbook_retrieval", runbook_retrieval)
    graph.add_node("root_cause", root_cause)
    graph.add_node("audit", audit)

    graph.add_edge(START, "intake")
    graph.add_conditional_edges(
        "intake", after_intake, ["log_analysis", "runbook_retrieval", "audit"]
    )
    # Dependency tracing starts from the first failure, so it waits for log analysis.
    graph.add_edge("log_analysis", "dependency_trace")
    # Root cause waits for both branches, so it reasons over all the evidence.
    graph.add_edge(["dependency_trace", "runbook_retrieval"], "root_cause")
    graph.add_edge("root_cause", "audit")
    graph.add_edge("audit", END)

    return graph.compile()


GRAPH = build_graph()


def new_investigation_id() -> str:
    return f"INVEST-{uuid4().hex[:12]}"


async def investigate(
    request: dict[str, Any],
    dependencies: Dependencies,
    *,
    investigation_id: str | None = None,
) -> dict[str, Any]:
    # The only entry point, so no caller can forget the dependencies.
    return await GRAPH.ainvoke(
        {
            "investigation_id": investigation_id or new_investigation_id(),
            "started_at": datetime.now(UTC),
            "request": request,
        },
        context=dependencies,
    )
