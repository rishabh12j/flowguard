from datetime import timedelta

from langgraph.runtime import Runtime

from flowguard.domain.evidence import EvidenceItem
from flowguard.graph.context import Dependencies, EvidenceUnavailable, Found
from flowguard.graph.state import InvestigationState

# A deployment can cause failures long after it finishes, so look back a full day.
LOOKBACK = timedelta(hours=24)


def services_at_or_upstream(dependency_map: EvidenceItem, service: str) -> set[str]:
    edges = dependency_map.metadata["edges"]
    found = {service}
    frontier = {service}
    while frontier:
        frontier = {edge["from"] for edge in edges if edge["to"] in frontier} - found
        found |= frontier
    return found


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
