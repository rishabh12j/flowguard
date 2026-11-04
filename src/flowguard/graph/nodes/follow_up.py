from langgraph.runtime import Runtime

from flowguard.graph.context import Dependencies
from flowguard.graph.state import InvestigationState


# Runs when a reviewer asks for more evidence. The reviewer's comment says what
# to look for, so it becomes a new search of the knowledge base, and the model
# sees it when it reasons again.
def follow_up(
    state: InvestigationState, runtime: Runtime[Dependencies]
) -> InvestigationState:
    decision = state.get("decision")
    if decision is None:
        raise ValueError("a follow-up needs the reviewer's decision")
    incident = state["incident"]
    found = runtime.context.retriever(decision.comment, system=incident.affected_system)
    known = {item.evidence_id for item in state.get("evidence", ())}
    return {
        "evidence": tuple(item for item in found if item.evidence_id not in known),
        "evidence_round": state.get("evidence_round", 0) + 1,
        "reviewer_request": decision.comment,
        # The new round reaches its own conclusions. The evidence, the errors, and
        # the saved versions of the record stay.
        "decision": None,
        "hypotheses": (),
        "selected_root_cause": None,
        "abstention": None,
        "proposed_actions": (),
        "actions": (),
        "rejected_actions": (),
        "plan_problems": (),
        "remediation_attempts": 0,
        "requires_approval": False,
    }
