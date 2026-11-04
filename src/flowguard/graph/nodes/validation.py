from flowguard.domain.validation import check_actions
from flowguard.graph.state import InvestigationState


# Deterministic: the same proposal and evidence always give the same plan.
def validation(state: InvestigationState) -> InvestigationState:
    root_cause = state.get("selected_root_cause")
    if root_cause is None:
        raise ValueError("routing sends only a selected root cause to validation")
    attempt = state.get("remediation_attempts", 1)
    planned, rejected = check_actions(
        state.get("proposed_actions", ()),
        state.get("evidence", ()),
        root_cause,
        attempt,
    )
    return {
        "actions": planned,
        # Earlier attempts' rejections stay in the record.
        "rejected_actions": (*state.get("rejected_actions", ()), *rejected),
        "plan_problems": tuple(
            f"{item.proposed.action} on {item.proposed.target}: {item.problem}"
            for item in rejected
        ),
        "requires_approval": any(action.requires_approval for action in planned),
    }
