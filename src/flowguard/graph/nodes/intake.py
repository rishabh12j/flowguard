from pydantic import ValidationError
from pydantic_core import ErrorDetails

from flowguard.domain.incidents import Incident
from flowguard.graph.state import InvestigationState


def describe(problem: ErrorDetails) -> str:
    # The message leaves out the rejected value, so a pasted secret never reaches the errors.
    field = ".".join(str(part) for part in problem["loc"]) or "request"
    return f"{field}: {problem['msg']}"


def intake(state: InvestigationState) -> InvestigationState:
    try:
        incident = Incident.model_validate(state.get("request", {}))
    except ValidationError as error:
        return {"errors": tuple(describe(problem) for problem in error.errors())}
    return {"incident": incident}
