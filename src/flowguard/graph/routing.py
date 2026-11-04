from flowguard.graph.state import InvestigationState


def after_intake(state: InvestigationState) -> list[str]:
    if "incident" not in state:
        # A rejected request is still part of the record.
        return ["audit"]
    # Logs and documents don't depend on each other, so they are gathered in parallel.
    return ["log_analysis", "runbook_retrieval"]
