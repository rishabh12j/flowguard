import operator
from datetime import datetime
from typing import Annotated, Any, TypedDict

from flowguard.domain.approval import ApprovalDecision
from flowguard.domain.audit import InvestigationStatus, ToolCallRecord
from flowguard.domain.evidence import EvidenceItem
from flowguard.domain.hypotheses import IncidentCategory, RootCauseHypothesis
from flowguard.domain.incidents import Incident
from flowguard.domain.remediation import (
    PlannedAction,
    ProposedAction,
    RejectedAction,
)


class InvestigationState(TypedDict, total=False):
    # Every key is optional because a node returns only the keys it changes.
    investigation_id: str
    started_at: datetime
    request: dict[str, Any]
    incident: Incident
    first_failure: EvidenceItem
    hypotheses: tuple[RootCauseHypothesis, ...]
    selected_root_cause: RootCauseHypothesis
    # The selected root cause's category, or unknown when FlowGuard abstains.
    category: IncidentCategory

    # Why no root cause was selected. Abstaining is a result, not an error.
    abstention: str
    status: InvestigationStatus
    proposed_actions: tuple[ProposedAction, ...]
    actions: tuple[PlannedAction, ...]
    rejected_actions: tuple[RejectedAction, ...]
    requires_approval: bool
    decision: ApprovalDecision
    # Kept by the audit node, so a resumed investigation continues its record.
    audit_version: int
    tool_calls: tuple[ToolCallRecord, ...]

    # These reducers join updates, so nodes running in parallel can all add to them.
    evidence: Annotated[tuple[EvidenceItem, ...], operator.add]
    errors: Annotated[tuple[str, ...], operator.add]
