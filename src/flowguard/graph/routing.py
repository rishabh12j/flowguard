from langgraph.graph import END

from flowguard.graph.state import InvestigationState


def after_intake(state: InvestigationState) -> str:
    return "runbook_retrieval" if "incident" in state else END
