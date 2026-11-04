from collections.abc import Sequence

from langgraph.runtime import Runtime

from flowguard.domain.evidence import EvidenceItem
from flowguard.graph.context import Dependencies, EvidenceUnavailable
from flowguard.graph.state import InvestigationState


def first_error(logs: Sequence[EvidenceItem]) -> EvidenceItem | None:
    errors = [
        (item.timestamp, item)
        for item in logs
        if item.metadata.get("level") == "ERROR" and item.timestamp is not None
    ]
    return min(errors, key=lambda pair: pair[0])[1] if errors else None


async def log_analysis(
    state: InvestigationState, runtime: Runtime[Dependencies]
) -> InvestigationState:
    incident = state["incident"]
    try:
        found = await runtime.context.tools.search_logs(
            incident.start_time, incident.end_time
        )
    except EvidenceUnavailable as error:
        return {"errors": (f"log_analysis: {error}",)}

    update: InvestigationState = {"evidence": tuple(found.items)}
    if found.truncated:
        update["errors"] = ("log_analysis: only the earliest logs were returned",)
    failure = first_error(found.items)
    if failure is not None:
        update["first_failure"] = failure
    return update
