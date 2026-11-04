from langgraph.runtime import Runtime

from flowguard.domain.causality import LOOKBACK, services_at_or_upstream
from flowguard.graph.context import Dependencies, EvidenceUnavailable, Found
from flowguard.graph.state import InvestigationState


async def dependency_trace(
    state: InvestigationState, runtime: Runtime[Dependencies]
) -> InvestigationState:
    incident = state["incident"]
    failure = state.get("first_failure")
    tools = runtime.context.tools

    # Without a failing log, the start of the incident window is the best anchor.
    if failure is not None and failure.timestamp is not None:
        anchor = failure.timestamp
    else:
        anchor = incident.start_time

    try:
        deployments = await tools.get_deployments(anchor - LOOKBACK, anchor)
        maps = (
            await tools.get_dependency_map(failure.source_name)
            if failure is not None
            else Found([])
        )
    except EvidenceUnavailable as error:
        return {"errors": (f"dependency_trace: {error}",)}

    suspects = deployments.items
    # A deployment downstream of the failure cannot have caused it. Without a
    # map, every deployment stays, because the dependency may be undocumented.
    if failure is not None and maps.items:
        possible: set[str] = set()
        for dependency_map in maps.items:
            possible |= services_at_or_upstream(dependency_map, failure.source_name)
        suspects = [item for item in suspects if item.source_name in possible]
    return {"evidence": (*maps.items, *suspects)}
