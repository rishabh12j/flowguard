from collections.abc import Sequence

from flowguard.domain.evidence import EvidenceItem
from flowguard.domain.hypotheses import RootCauseHypothesis
from flowguard.domain.remediation import (
    CATALOGUE,
    PlannedAction,
    ProposedAction,
    RejectedAction,
    TargetKind,
)


def targets_in(evidence: Sequence[EvidenceItem]) -> dict[TargetKind, set[str]]:
    """What an action may target: services that logged or were deployed, and deployments."""
    return {
        "service": {
            item.source_name
            for item in evidence
            if item.source_type in ("log", "deployment")
        },
        "deployment": {
            item.evidence_id for item in evidence if item.source_type == "deployment"
        },
    }


def grounds_for_action(
    evidence: Sequence[EvidenceItem], root_cause: RootCauseHypothesis
) -> set[str]:
    """Evidence that can justify a step: the diagnosis, or advice on how to fix it."""
    guidance = {
        item.evidence_id
        for item in evidence
        if item.source_type in ("runbook", "historical_incident")
    }
    return set(root_cause.supporting_evidence_ids) | guidance


def problem_with(
    proposed: ProposedAction,
    evidence_ids: set[str],
    grounds: set[str],
    targets: dict[TargetKind, set[str]],
    cause_fixed: bool,
) -> str | None:
    spec = CATALOGUE.get(proposed.action)
    if spec is None:
        return "not an allowed action"
    unknown = sorted(set(proposed.evidence_ids) - evidence_ids)
    if unknown:
        return f"cites unknown evidence: {unknown}"
    if not set(proposed.evidence_ids) & grounds:
        return "cites neither the root cause's evidence nor a runbook or past incident"
    if proposed.target not in targets[spec.target]:
        return f"its target is not a {spec.target} in the evidence"
    if spec.requires_fix_first and not cause_fixed:
        return "must come after a step that fixes the cause"
    return None


def check_actions(
    proposed: Sequence[ProposedAction],
    evidence: Sequence[EvidenceItem],
    root_cause: RootCauseHypothesis,
) -> tuple[tuple[PlannedAction, ...], tuple[RejectedAction, ...]]:
    evidence_ids = {item.evidence_id for item in evidence}
    grounds = grounds_for_action(evidence, root_cause)
    targets = targets_in(evidence)
    planned: list[PlannedAction] = []
    rejected: list[RejectedAction] = []
    cause_fixed = False

    for action in proposed:
        problem = problem_with(action, evidence_ids, grounds, targets, cause_fixed)
        if problem is not None:
            rejected.append(RejectedAction(proposed=action, problem=problem))
            continue
        spec = CATALOGUE[action.action]
        # Only a step that passed counts as a fix, so a rejected fix can't unlock a replay.
        cause_fixed = cause_fixed or spec.fixes_cause
        planned.append(
            PlannedAction(
                **action.model_dump(),
                step=len(planned) + 1,
                kind=spec.kind,
                # Risk and approval come from the catalogue, never from the model.
                risk=spec.risk,
                changes_state=spec.changes_state,
                requires_approval=spec.requires_approval,
                rollback=spec.rollback,
                verification=spec.verification,
            )
        )
    return tuple(planned), tuple(rejected)
