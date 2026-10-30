from typing import Any, Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

SourceType = Literal[
    "log",
    "metric",
    "alert",
    "runbook",
    "api_spec",
    "deployment",
    "dependency_map",
    "historical_incident",
]


class EvidenceItem(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    evidence_id: str = Field(pattern=r"^\S+$")
    source_type: SourceType
    source_name: str
    timestamp: AwareDatetime | None = None
    title: str
    content: str
    metadata: dict[str, Any]
    # Retrievers must convert scores to 0-1 before creating evidence.
    retrieval_score: float | None = Field(default=None, ge=0, le=1)
    correlation_id: str | None = None
