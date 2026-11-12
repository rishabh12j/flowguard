from collections.abc import Sequence
from datetime import UTC, datetime

from langgraph.runtime import Runtime

from flowguard.domain.approval import Decision
from flowguard.domain.audit import (
    InvestigationRecord,
    InvestigationStatus,
    ToolCallRecord,
)
from flowguard.graph.context import Dependencies
from flowguard.graph.state import InvestigationState

DECIDED: dict[Decision, InvestigationStatus] = {
    "approve": "approved",
    "reject": "declined",
    "request_more_evidence": "more_evidence_requested",
}


def status_of(state: InvestigationState) -> InvestigationStatus:
    decision = state.get("decision")
    if "incident" not in state:
        return "rejected"
    if state.get("selected_root_cause") is None:
        return "abstained"
    if decision is not None:
        return DECIDED[decision.decision]
    if state.get("requires_approval", False):
        return "awaiting_approval"
    return "diagnosed"


def build_record(
    state: InvestigationState,
    tool_calls: Sequence[ToolCallRecord],
    finished_at: datetime,
) -> InvestigationRecord:
    selected = state.get("selected_root_cause")
    return InvestigationRecord(
        investigation_id=state["investigation_id"],
        version=state.get("audit_version", 0) + 1,
        status=status_of(state),
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
        actions=state.get("actions", ()),
        rejected_actions=state.get("rejected_actions", ()),
        requires_approval=state.get("requires_approval", False),
        decision=state.get("decision"),
        evidence_round=state.get("evidence_round", 0),
        reviewer_request=state.get("reviewer_request"),
        evidence_score=state.get("evidence_score"),
        missing_sources=state.get("missing_sources", 0),
        decision_rule=state.get("decision_rule"),
        root_cause_service=state.get("root_cause_service"),
        located=state.get("located", False),
    )


# If the record can't be saved, this raises and the investigation fails. An
# unaudited result is worse than a visible error.
def audit(
    state: InvestigationState, runtime: Runtime[Dependencies]
) -> InvestigationState:
    # Calls made before a pause are in the state. The tools of the request that
    # resumed the investigation only know their own calls.
    tool_calls = (*state.get("tool_calls", ()), *runtime.context.tools.history)
    record = build_record(state, tool_calls, datetime.now(UTC))
    runtime.context.audit.save(record)
    return {
        "status": record.status,
        "audit_version": record.version,
        "tool_calls": record.tool_calls,
    }
