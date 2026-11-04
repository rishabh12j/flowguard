from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from flowguard.graph.context import Dependencies
from flowguard.graph.nodes.dependency_trace import dependency_trace
from flowguard.graph.nodes.intake import intake
from flowguard.graph.nodes.log_analysis import log_analysis
from flowguard.graph.nodes.retrieval import runbook_retrieval
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
    graph.add_edge(START, "intake")
    graph.add_conditional_edges(
        "intake", after_intake, ["log_analysis", "runbook_retrieval", END]
    )
    # Dependency tracing starts from the first failure, so it waits for log analysis.
    graph.add_edge("log_analysis", "dependency_trace")
    graph.add_edge("dependency_trace", END)
    graph.add_edge("runbook_retrieval", END)
    return graph.compile()


GRAPH = build_graph()


async def investigate(
    request: dict[str, Any], dependencies: Dependencies
) -> dict[str, Any]:
    # The only entry point, so no caller can forget the dependencies.
    return await GRAPH.ainvoke({"request": request}, context=dependencies)
