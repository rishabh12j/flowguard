from langgraph.runtime import Runtime

from flowguard.graph.context import Dependencies, EvidenceUnavailable, Found
from flowguard.graph.state import InvestigationState


# Runs when a reviewer asks for more evidence. The reviewer's comment says what
# to look for, so it becomes a new search of the knowledge base, and the model
# sees it when it reasons again.
async def follow_up(
    state: InvestigationState, runtime: Runtime[Dependencies]
) -> InvestigationState:
    decision = state.get("decision")
    if decision is None:
        raise ValueError("a follow-up needs the reviewer's decision")
    incident = state["incident"]
    errors: tuple[str, ...] = ()
    try:
        found = await runtime.context.tools.search_runbooks(
            decision.comment, incident.affected_system
        )
    except EvidenceUnavailable as error:
        # The round goes ahead with the evidence it has, and records the gap.
        found, errors = Found([]), (f"follow_up: {error}",)
    known = {item.evidence_id for item in state.get("evidence", ())}
    return {
        "evidence": tuple(
            item for item in found.items if item.evidence_id not in known
        ),
        "errors": errors,
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
