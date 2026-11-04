from flowguard.domain.validation import check_actions
from flowguard.graph.state import InvestigationState


# Deterministic: the same proposal and evidence always give the same plan.
def validation(state: InvestigationState) -> InvestigationState:
    planned, rejected = check_actions(
        state.get("proposed_actions", ()),
        state.get("evidence", ()),
        state["selected_root_cause"],
    )
    return {
        "actions": planned,
        "rejected_actions": rejected,
        "requires_approval": any(action.requires_approval for action in planned),
    }
