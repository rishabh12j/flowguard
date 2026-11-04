import operator
from typing import Annotated, Any, TypedDict

from flowguard.domain.evidence import EvidenceItem
from flowguard.domain.incidents import Incident
from flowguard.domain.hypotheses import RootCauseHypothesis


class InvestigationState(TypedDict, total=False):
    # Every key is optional because a node returns only the keys it changes.
    request: dict[str, Any]
    incident: Incident
    first_failure: EvidenceItem
    hypotheses: tuple[RootCauseHypothesis, ...]
    selected_root_cause: RootCauseHypothesis
    # Why no root cause was selected. Abstaining is a result, not an error.
    abstention: str

    # These reducers join updates, so nodes running in parallel can all add to them.
    evidence: Annotated[tuple[EvidenceItem, ...], operator.add]
    errors: Annotated[tuple[str, ...], operator.add]
