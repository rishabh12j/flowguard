from collections.abc import Iterable
from datetime import datetime
from typing import Annotated, Any, TypedDict, TypeVar

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

Item = TypeVar("Item")


def joined(existing: Iterable[Item], new: Iterable[Item]) -> tuple[Item, ...]:
    # A checkpoint stores tuples as lists, so after a resume the existing value is
    # a list. operator.add can't join a list and a tuple; this joins anything.
    return (*existing, *new)


class InvestigationState(TypedDict, total=False):
    # Every key is optional because a node returns only the keys it changes.
    investigation_id: str
    started_at: datetime
    request: dict[str, Any]
    incident: Incident
    first_failure: EvidenceItem
    hypotheses: tuple[RootCauseHypothesis, ...]
    # None again when a follow-up round starts, until a root cause is selected.
    selected_root_cause: RootCauseHypothesis | None
    # The selected root cause's category, or unknown when FlowGuard abstains.
    category: IncidentCategory

    # Why no root cause was selected. Abstaining is a result, not an error.
    abstention: str | None
    # The rubric's score of all the cited evidence together, the evidence sources
    # that failed, and the decision rule that chose the answer.
    evidence_score: float
    missing_sources: int
    decision_rule: str
    status: InvestigationStatus
    proposed_actions: tuple[ProposedAction, ...]
    actions: tuple[PlannedAction, ...]
    # Every rejection in this round, from every attempt.
    rejected_actions: tuple[RejectedAction, ...]
    # What was wrong with the latest attempt, shown to the model if it tries again.
    plan_problems: tuple[str, ...]
    remediation_attempts: int
    requires_approval: bool
    decision: ApprovalDecision | None
    # How many follow-up rounds a reviewer has asked for, and what they asked.
    evidence_round: int
    reviewer_request: str | None
    # Kept by the audit node, so a resumed investigation continues its record.
    audit_version: int
    tool_calls: tuple[ToolCallRecord, ...]

    # These reducers join updates, so nodes running in parallel can all add to them.
    evidence: Annotated[tuple[EvidenceItem, ...], joined]
    errors: Annotated[tuple[str, ...], joined]
