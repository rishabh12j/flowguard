from langgraph.graph import END

from flowguard.graph.state import InvestigationState

# A plan whose every step was refused gets one more attempt, with the reasons.
MAX_PLAN_ATTEMPTS = 2
# A reviewer can send an investigation back for more evidence once.
MAX_EVIDENCE_ROUNDS = 1


def after_intake(state: InvestigationState) -> list[str]:
    if "incident" not in state:
        # A rejected request is still part of the record.
        return ["audit"]
    # Logs and documents don't depend on each other, so they are gathered in parallel.
    return ["log_analysis", "runbook_retrieval"]


def after_root_cause(state: InvestigationState) -> str:
    # Actions are only proposed for a confirmed root cause.
    return "remediation" if state.get("selected_root_cause") is not None else "audit"


def after_validation(state: InvestigationState) -> str:
    nothing_left = not state.get("actions") and state.get("plan_problems")
    if nothing_left and state.get("remediation_attempts", 1) < MAX_PLAN_ATTEMPTS:
        return "remediation"
    return "audit"


def after_audit(state: InvestigationState) -> str:
    # Only a saved plan that needs approval waits for a person.
    if state.get("status") == "awaiting_approval":
        return "approval"
    if (
        state.get("status") == "more_evidence_requested"
        and state.get("evidence_round", 0) < MAX_EVIDENCE_ROUNDS
    ):
        return "follow_up"
    return END
