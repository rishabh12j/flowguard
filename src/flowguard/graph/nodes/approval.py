from langgraph.types import interrupt

from flowguard.domain.approval import ApprovalDecision
from flowguard.graph.state import InvestigationState


# The graph stops at interrupt() until a person decides. Resuming runs this node
# again from the top, so nothing before interrupt() may have side effects.
def approval(state: InvestigationState) -> InvestigationState:
    answer = interrupt(
        {
            "steps_needing_approval": [
                action.step for action in state["actions"] if action.requires_approval
            ]
        }
    )
    # The decision came from outside the graph, so it is validated like any input.
    return {"decision": ApprovalDecision.model_validate(answer)}
