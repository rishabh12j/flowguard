from langgraph.runtime import Runtime

from flowguard.graph.context import Dependencies, EvidenceUnavailable
from flowguard.graph.state import InvestigationState


async def runbook_retrieval(
    state: InvestigationState, runtime: Runtime[Dependencies]
) -> InvestigationState:
    incident = state["incident"]
    try:
        found = await runtime.context.tools.search_runbooks(
            incident.description, incident.affected_system
        )
    except EvidenceUnavailable as error:
        return {"errors": (f"runbook_retrieval: {error}",)}
    return {"evidence": tuple(found.items)}
