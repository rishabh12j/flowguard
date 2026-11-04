from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

# The brief's incident categories.
IncidentCategory = Literal[
    "authentication",
    "authorisation",
    "schema_contract_mismatch",
    "networking",
    "timeout",
    "rate_limiting",
    "data_quality",
    "file_transfer",
    "queue_or_event_processing",
    "deployment_or_configuration",
    "unknown",
]

# A label without a definition is ambiguous, so the model is given both.
CATEGORY_DEFINITIONS: dict[IncidentCategory, str] = {
    "authentication": "a caller's identity could not be verified, such as an expired credential or token",
    "authorisation": "a known caller was refused access it needs",
    "schema_contract_mismatch": "data was rejected because its structure, such as field names, types, or required fields, does not match the contract the receiver checks",
    "networking": "systems could not reach each other, such as DNS, refused connections, or TLS failures",
    "timeout": "a call or job took longer than it was allowed",
    "rate_limiting": "requests were rejected for exceeding a quota or rate",
    "data_quality": "data had the expected structure but wrong, missing, or inconsistent values",
    "file_transfer": "a file was not delivered, picked up, or read correctly",
    "queue_or_event_processing": "messages were stuck, lost, duplicated, or processed out of order",
    "deployment_or_configuration": "a released change or setting is itself faulty, and no other category describes the failure",
    "unknown": "the evidence does not show which category applies",
}


class ProposedHypothesis(BaseModel):
    """A root cause suggested by the model, before code scores its confidence."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    description: str = Field(min_length=1)
    category: IncidentCategory

    supporting_evidence_ids: tuple[str, ...] = Field(min_length=1)
    contradicting_evidence_ids: tuple[str, ...]
    missing_evidence: tuple[str, ...]

    @model_validator(mode="after")
    def evidence_is_not_on_both_sides(self) -> "ProposedHypothesis":
        both = set(self.supporting_evidence_ids) & set(self.contradicting_evidence_ids)
        if both:
            raise ValueError(f"evidence both supports and contradicts: {sorted(both)}")
        return self


class HypothesisProposal(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    hypotheses: tuple[ProposedHypothesis, ...] = Field(min_length=1, max_length=3)


class RootCauseHypothesis(ProposedHypothesis):
    """A proposed hypothesis after code has scored its confidence."""

    hypothesis_id: str = Field(pattern=r"^\S+$")
    confidence: float = Field(ge=0, le=1)
    confidence_reason: str
