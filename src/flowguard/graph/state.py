import operator
from datetime import datetime
from typing import Annotated, Any, TypedDict

from flowguard.domain.audit import InvestigationStatus
from flowguard.domain.evidence import EvidenceItem
from flowguard.domain.hypotheses import IncidentCategory, RootCauseHypothesis
from flowguard.domain.incidents import Incident


class InvestigationState(TypedDict, total=False):
    # Every key is optional because a node returns only the keys it changes.

    investigation_id: str
    started_at: datetime
    request: dict[str, Any]
    incident: Incident
    first_failure: EvidenceItem
    hypotheses: tuple[RootCauseHypothesis, ...]
    selected_root_cause: RootCauseHypothesis
    # The selected root cause's category, or unknown when FlowGuard abstains.
    category: IncidentCategory

    # Why no root cause was selected. Abstaining is a result, not an error.
    abstention: str

    # These reducers join updates, so nodes running in parallel can all add to them.
    evidence: Annotated[tuple[EvidenceItem, ...], operator.add]
    errors: Annotated[tuple[str, ...], operator.add]
    status: InvestigationStatus
