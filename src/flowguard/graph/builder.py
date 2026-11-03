from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from flowguard.graph.context import Dependencies
from flowguard.graph.nodes.intake import intake
from flowguard.graph.nodes.retrieval import runbook_retrieval
from flowguard.graph.routing import after_intake
from flowguard.graph.state import InvestigationState

InvestigationGraph = CompiledStateGraph[
    InvestigationState, Dependencies, InvestigationState, InvestigationState
]


def build_graph() -> InvestigationGraph:
    graph = StateGraph(InvestigationState, context_schema=Dependencies)
    graph.add_node("intake", intake)
    graph.add_node("runbook_retrieval", runbook_retrieval)
    graph.add_edge(START, "intake")
    graph.add_conditional_edges("intake", after_intake, ["runbook_retrieval", END])
    graph.add_edge("runbook_retrieval", END)
    return graph.compile()


GRAPH = build_graph()


def investigate(request: dict[str, Any], dependencies: Dependencies) -> dict[str, Any]:
    # The only entry point, so no caller can forget the dependencies.
    return GRAPH.invoke({"request": request}, context=dependencies)
