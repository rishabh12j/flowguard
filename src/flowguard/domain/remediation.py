from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Risk = Literal["low", "medium", "high"]
TargetKind = Literal["service", "deployment"]


class ActionSpec(BaseModel):
    """An action FlowGuard may recommend, with the safeguards code attaches to it."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(pattern=r"^[a-z_]+$")
    purpose: str
    kind: Literal["mitigation", "corrective"]
    target: TargetKind
    changes_state: bool
    risk: Risk
    # True when the action removes the cause, so steps that depend on a fix can follow.
    fixes_cause: bool = False
    requires_fix_first: bool = False
    rollback: str = ""
    verification: str = Field(min_length=1)

    @model_validator(mode="after")
    def state_changes_can_be_rolled_back(self) -> "ActionSpec":
        if self.changes_state and not self.rollback:
            raise ValueError(f"{self.name} changes state, so it needs a rollback step")
        return self

    @property
    def requires_approval(self) -> bool:
        # In the MVP, a person approves every change to a running system.
        return self.changes_state


CATALOGUE = {
    spec.name: spec
    for spec in (
        ActionSpec(
            name="update_field_mapping",
            purpose="change how a service maps incoming fields to the contract it sends on",
            kind="mitigation",
            target="service",
            changes_state=True,
            risk="medium",
            fixes_cause=True,
            rollback="Redeploy the previous mapping version.",
            verification="Send a sample of the failed payloads through the new mapping "
            "and confirm they pass validation.",
        ),
        ActionSpec(
            name="rollback_deployment",
            purpose="return a service to the version before a deployment",
            kind="mitigation",
            target="deployment",
            changes_state=True,
            risk="high",
            fixes_cause=True,
            rollback="Redeploy the version that was rolled back.",
            verification="Confirm the service runs the previous version and the "
            "errors stop.",
        ),
        ActionSpec(
            name="replay_failed_messages",
            purpose="resend the messages a service failed to process, from its "
            "dead-letter queue",
            kind="mitigation",
            target="service",
            changes_state=True,
            risk="high",
            requires_fix_first=True,
            rollback="A replay can't be undone. Stop the replay and leave the "
            "remaining messages in the queue.",
            verification="Confirm each replayed message was processed once and the "
            "queue is empty.",
        ),
        ActionSpec(
            name="add_contract_test",
            purpose="add a test to a service's deployment pipeline that rejects "
            "payloads breaking the contract",
            kind="corrective",
            target="service",
            changes_state=False,
            risk="low",
            verification="Confirm the test fails on the faulty payload and passes on "
            "a correct one.",
        ),
        ActionSpec(
            name="notify_service_owner",
            purpose="tell the team that owns a service what happened and what it "
            "needs to change",
            kind="corrective",
            target="service",
            changes_state=False,
            risk="low",
            verification="Confirm the owning team has acknowledged the incident.",
        ),
        ActionSpec(
            name="rotate_credential",
            purpose="replace an expired or leaked credential that a service uses, "
            "through the secrets manager",
            kind="mitigation",
            target="service",
            changes_state=True,
            risk="high",
            fixes_cause=True,
            rollback="Restore the previous credential version in the secrets manager "
            "if the provider rejects the new one.",
            verification="Confirm a test request to the provider succeeds with the "
            "new credential.",
        ),
        ActionSpec(
            name="rerun_job",
            purpose="run a failed scheduled job again for the periods it missed",
            kind="mitigation",
            target="service",
            changes_state=True,
            risk="medium",
            requires_fix_first=True,
            rollback="Stop the run and discard what it wrote to staging.",
            verification="Confirm the job completed for every missed period, with no "
            "duplicate records.",
        ),
        ActionSpec(
            name="pause_job",
            purpose="pause a scheduled or batch job that is overloading another service",
            kind="mitigation",
            target="service",
            changes_state=True,
            risk="medium",
            fixes_cause=True,
            rollback="Resume the job.",
            verification="Confirm the overloaded service's request rate has dropped "
            "below its limit.",
        ),
        ActionSpec(
            name="enable_rate_limiting",
            purpose="limit how fast a service sends requests to a provider, so it "
            "stays within the provider's quota",
            kind="corrective",
            target="service",
            changes_state=True,
            risk="medium",
            fixes_cause=True,
            rollback="Remove the limit, returning to the previous request rate.",
            verification="Confirm requests stay below the provider's limit and no 429 "
            "responses occur.",
        ),
        ActionSpec(
            name="redeliver_file",
            purpose="deliver a file again, to the place its receiver reads from",
            kind="mitigation",
            target="service",
            changes_state=True,
            risk="medium",
            requires_fix_first=True,
            rollback="Remove the redelivered file before the receiver picks it up.",
            verification="Confirm the receiver acknowledged the file exactly once.",
        ),
        ActionSpec(
            name="add_monitoring",
            purpose="add an alert or check that would catch this failure earlier",
            kind="corrective",
            target="service",
            changes_state=False,
            risk="low",
            verification="Confirm the new alert or check fires in a test.",
        ),
    )
}


class ProposedAction(BaseModel):
    """A step suggested by the model, before code checks it against the catalogue."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    # A plain string, not the catalogue's names, so validation is the one place an
    # unknown action is refused, and the refusal is recorded.
    action: str = Field(min_length=1)
    target: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    evidence_ids: tuple[str, ...] = Field(min_length=1)


class RemediationProposal(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    actions: tuple[ProposedAction, ...] = Field(min_length=1, max_length=5)


class PlannedAction(ProposedAction):
    """A step that passed validation, with its risk and safeguards from the catalogue."""

    step: int = Field(ge=1)
    kind: Literal["mitigation", "corrective"]
    risk: Risk
    changes_state: bool
    requires_approval: bool
    rollback: str
    verification: str


class RejectedAction(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    proposed: ProposedAction
    problem: str
    # Which attempt at a plan proposed it. A plan with nothing left is retried.
    attempt: int = Field(default=1, ge=1)
