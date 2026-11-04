from collections.abc import Awaitable

from langgraph.runtime import Runtime

from flowguard.domain.causality import LOOKBACK, services_at_or_upstream
from flowguard.domain.evidence import EvidenceItem
from flowguard.graph.context import Dependencies, EvidenceUnavailable, Found
from flowguard.graph.state import InvestigationState


# Gathers the changes that could explain the first failure: deployments, alerts,
# and metrics, from the day before it, in the failing service or upstream of it.
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
    start = anchor - LOOKBACK
    errors: list[str] = []

    async def fetch(call: Awaitable[Found]) -> list[EvidenceItem]:
        # One tool failing loses only its own evidence.
        try:
            return (await call).items
        except EvidenceUnavailable as error:
            errors.append(f"dependency_trace: {error}")
            return []

    deployments = await fetch(tools.get_deployments(start, anchor))
    alerts = await fetch(tools.search_alerts(start, anchor))
    maps = (
        await fetch(tools.get_dependency_map(failure.source_name))
        if failure is not None
        else []
    )

    # A change downstream of the failure cannot have caused it. Without a map,
    # every change stays, because the dependency may be undocumented.
    upstream: set[str] | None = None
    if failure is not None and maps:
        upstream = set()
        for dependency_map in maps:
            upstream |= services_at_or_upstream(dependency_map, failure.source_name)
    changes = [
        item
        for item in (*deployments, *alerts)
        if upstream is None or item.source_name in upstream
    ]

    # Metrics are kept per service, so ask for the failing service and everything
    # upstream of it.
    if upstream is not None:
        services = sorted(upstream)
    elif failure is not None:
        services = [failure.source_name]
    else:
        services = []
    metrics = []
    for service in services:
        metrics += await fetch(tools.get_metrics(service, start, anchor))

    return {"evidence": (*maps, *changes, *metrics), "errors": tuple(errors)}
