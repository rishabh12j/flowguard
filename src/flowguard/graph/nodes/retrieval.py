from langgraph.runtime import Runtime

from flowguard.graph.context import Dependencies
from flowguard.graph.state import InvestigationState


def runbook_retrieval(
    state: InvestigationState, runtime: Runtime[Dependencies]
) -> InvestigationState:
    incident = state["incident"]
    documents = runtime.context.retriever(
        incident.description, system=incident.affected_system
    )
    return {"evidence": tuple(documents)}
