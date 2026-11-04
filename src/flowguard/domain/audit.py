from typing import Any, Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from flowguard.domain.approval import ApprovalDecision
from flowguard.domain.hypotheses import IncidentCategory, RootCauseHypothesis
from flowguard.domain.incidents import Incident
from flowguard.domain.remediation import PlannedAction, RejectedAction

InvestigationStatus = Literal[
    "diagnosed",
    "abstained",
    "rejected",
    "awaiting_approval",
    "approved",
    "declined",
    "more_evidence_requested",
]
ToolOutcome = Literal["ok", "denied", "failed"]


class DuplicateVersion(Exception):
    """This version of the investigation's record was already saved."""


class ToolCallRecord(BaseModel):
    """One tool call, as the tool layer saw it, including calls that were refused."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    tool: str
    arguments: dict[str, Any]
    outcome: ToolOutcome
    detail: str = ""
    items: int = Field(default=0, ge=0)
    truncated: bool = False
    seconds: float = Field(ge=0)


class InvestigationRecord(BaseModel):
    """Everything needed to see what an investigation did and why."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    investigation_id: str = Field(pattern=r"^\S+$")
    # Each save adds a version. Earlier versions are never changed.
    version: int = Field(default=1, ge=1)
    status: InvestigationStatus
    started_at: AwareDatetime
    # When this version was saved.
    finished_at: AwareDatetime
    # The validated incident, never the raw request, which could hold anything.
    incident: Incident | None
    category: IncidentCategory | None
    evidence_ids: tuple[str, ...]
    tool_calls: tuple[ToolCallRecord, ...]
    hypotheses: tuple[RootCauseHypothesis, ...]
    selected_hypothesis_id: str | None
    abstention: str | None
    errors: tuple[str, ...]
    # Defaults, so records saved before remediation existed still load.
    actions: tuple[PlannedAction, ...] = ()
    rejected_actions: tuple[RejectedAction, ...] = ()
    requires_approval: bool = False
    decision: ApprovalDecision | None = None
