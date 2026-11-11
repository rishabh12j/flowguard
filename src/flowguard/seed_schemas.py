"""The shape of every seeded data file. The loader checks each record against these,
so a mistake in the data fails loudly instead of skewing an investigation."""

from datetime import date
from typing import Any, Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator

from flowguard.domain.hypotheses import IncidentCategory

Identifier = Field(pattern=r"^\S+$")


class Record(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class LogRecord(Record):
    event_id: str = Identifier
    timestamp: AwareDatetime
    service: str = Identifier
    environment: str
    level: Literal["DEBUG", "INFO", "WARN", "ERROR"]
    correlation_id: str = Identifier
    message: str = Field(min_length=1)
    exception_type: str | None
    metadata: dict[str, Any]


class DeploymentRecord(Record):
    deployment_id: str = Identifier
    service: str = Identifier
    version: str
    timestamp: AwareDatetime
    changes: list[str] = Field(min_length=1)
    status: Literal["successful", "failed", "rolled_back"]


class AlertRecord(Record):
    alert_id: str = Identifier
    service: str = Identifier
    fired_at: AwareDatetime
    severity: Literal["info", "warning", "critical"]
    status: Literal["firing", "resolved"]
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)


class MetricPoint(Record):
    timestamp: AwareDatetime
    value: float


class MetricSeries(Record):
    series_id: str = Identifier
    service: str = Identifier
    metric: str = Identifier
    unit: str
    threshold: float
    points: list[MetricPoint] = Field(min_length=1)

    @model_validator(mode="after")
    def points_are_in_time_order(self) -> "MetricSeries":
        times = [point.timestamp for point in self.points]
        if times != sorted(times) or len(set(times)) != len(times):
            raise ValueError("points must be in time order, one per timestamp")
        return self


class MapNode(Record):
    name: str = Identifier
    type: Literal["api", "service", "job", "queue", "database", "sftp"]


class MapEdge(Record):
    # An edge from A to B means B depends on A: A's data or answers flow to B.
    # So a failure can be caused at the failing service or anywhere upstream.
    model_config = ConfigDict(frozen=True, extra="forbid", populate_by_name=True)

    source: str = Field(alias="from")
    to: str


class DependencyMapRecord(Record):
    map_id: str = Identifier
    system: str = Identifier
    nodes: list[MapNode] = Field(min_length=1)
    edges: list[MapEdge]

    @model_validator(mode="after")
    def edges_join_known_nodes(self) -> "DependencyMapRecord":
        names = {node.name for node in self.nodes}
        unknown = {
            name for edge in self.edges for name in (edge.source, edge.to)
        } - names
        if unknown:
            raise ValueError(f"edges name unknown nodes: {sorted(unknown)}")
        return self


class DocumentHeader(Record):
    document_id: str = Identifier
    document_type: Literal["api_spec", "runbook", "historical_incident"]
    title: str = Field(min_length=1)
    system: str = Identifier
    service: str = Identifier
    version: str
    effective_date: date
    is_current: bool


class PlanStep(Record):
    action: str = Identifier
    target: str = Identifier


class GroundTruth(Record):
    incident_id: str = Identifier
    # Held-out incidents are evaluated once and never used to tune FlowGuard.
    split: Literal["tuning", "held_out", "dev", "test"] = "tuning"
    # The benchmark's scenario family, when the incident was generated.
    family: str | None = None
    # Since the benchmark from seed 2031: whether a change came before the failure,
    # the failure had a cause with nothing changed before it, or there was no
    # diagnosable cause; and whether the knowledge base has a runbook and a past
    # incident for this kind of failure.
    group: Literal["change", "nothing_changed", "no_cause"] | None = None
    precedent: bool | None = None
    # Some incidents have no supportable root cause: the right answer is to abstain.
    expected_outcome: Literal["diagnose", "abstain"] = "diagnose"
    category: IncidentCategory
    root_cause: str = Field(min_length=1)
    required_evidence_ids: list[str] = Field(min_length=1)
    # Other evidence that genuinely supports the diagnosis, such as further error
    # logs or the runbook. Citing it doesn't count against evidence precision.
    relevant_evidence_ids: list[str] = []
    acceptable_remediations: list[str] = Field(min_length=1)
    unsafe_actions: list[str]
    expected_approval_required: bool
    reference_plan: list[PlanStep] = []
    # Since 2026-11-11: the service the cause lies in, for incidents converted from
    # benchmarks that label one, such as RCAEval.
    root_cause_service: str | None = None

    @model_validator(mode="after")
    def a_diagnosis_has_a_plan(self) -> "GroundTruth":
        if self.expected_outcome == "diagnose" and not self.reference_plan:
            raise ValueError("an incident to diagnose needs a reference plan")
        return self
