from langgraph.graph import END

from flowguard.graph.state import InvestigationState


def after_intake(state: InvestigationState) -> list[str]:
    if "incident" not in state:
        # A rejected request is still part of the record.
        return ["audit"]
    # Logs and documents don't depend on each other, so they are gathered in parallel.
    return ["log_analysis", "runbook_retrieval"]


def after_root_cause(state: InvestigationState) -> str:
    # Actions are only proposed for a confirmed root cause.
    return "remediation" if "selected_root_cause" in state else "audit"


def after_audit(state: InvestigationState) -> str:
    # Only a saved plan that needs approval waits for a person. Everything else ends.
    return "approval" if state.get("status") == "awaiting_approval" else END
