from collections.abc import Sequence
from datetime import UTC, datetime

from langgraph.runtime import Runtime

from flowguard.domain.audit import (
    InvestigationRecord,
    InvestigationStatus,
    ToolCallRecord,
)
from flowguard.graph.context import Dependencies
from flowguard.graph.state import InvestigationState


def build_record(
    state: InvestigationState,
    tool_calls: Sequence[ToolCallRecord],
    finished_at: datetime,
) -> InvestigationRecord:
    selected = state.get("selected_root_cause")
    status: InvestigationStatus
    if "incident" not in state:
        status = "rejected"
    elif selected is not None:
        status = "diagnosed"
    else:
        status = "abstained"

    return InvestigationRecord(
        investigation_id=state["investigation_id"],
        status=status,
        started_at=state["started_at"],
        finished_at=finished_at,
        incident=state.get("incident"),
        category=state.get("category"),
        evidence_ids=tuple(item.evidence_id for item in state.get("evidence", ())),
        tool_calls=tuple(tool_calls),
        hypotheses=state.get("hypotheses", ()),
        selected_hypothesis_id=selected.hypothesis_id if selected else None,
        abstention=state.get("abstention"),
        errors=state.get("errors", ()),
    )


# If the record can't be saved, this raises and the investigation fails. An
# unaudited result is worse than a visible error.
def audit(
    state: InvestigationState, runtime: Runtime[Dependencies]
) -> InvestigationState:
    record = build_record(state, runtime.context.tools.history, datetime.now(UTC))
    runtime.context.audit.save(record)
    return {"status": record.status}
