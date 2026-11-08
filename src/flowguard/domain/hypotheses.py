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
    "timeout": "a call or job took longer than it was allowed, including waiting too long for a connection or another limited resource",
    "rate_limiting": "requests were rejected for exceeding a quota or rate",
    "data_quality": "data had the expected structure but wrong, missing, or inconsistent values",
    "file_transfer": "a file was not delivered, picked up, or read correctly, including a file sent to the wrong place",
    "queue_or_event_processing": "messages were stuck, lost, duplicated, or processed out of order",
    "deployment_or_configuration": "a released change or setting is broken in itself, such as a service that will not start; if a change made something else go wrong, use the category of what went wrong",
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


# What the check says the evidence shows about a hypothesis: that its category is
# what failed, only that a change came before the failure, or neither.
Verdict = Literal["mechanism", "trigger_only", "not_supported"]
VERDICT_MEANING: dict[Verdict, str] = {
    "mechanism": "the evidence shows this category is what failed",
    "trigger_only": "the evidence shows a change came before the failure, but not that this is what failed",
    "not_supported": "the evidence doesn't show this",
}


class RootCauseHypothesis(ProposedHypothesis):
    """A proposed hypothesis after code has scored its confidence."""

    hypothesis_id: str = Field(pattern=r"^\S+$")
    # How far its support leads the best hypothesis of another category.
    confidence: float = Field(ge=0, le=1)
    confidence_reason: str
    # The rubric's score of its evidence, which ranks hypotheses and decides
    # whether to abstain. None in records from before 2026-11-07, when the
    # confidence was this score.
    support: float | None = Field(default=None, ge=0, le=1)

    # Recorded since 2026-11-08, so each decision rule can be re-scored from one
    # run. All default to empty, so older records still load.
    # Where the model put it, 1 for its first choice. The list above is code's order.
    proposed_rank: int | None = Field(default=None, ge=1)
    # The rubric's signals its cited evidence shows, such as "error_log".
    signals: tuple[str, ...] = ()
    # How closely the incident's error logs match this category's definition.
    fit: float | None = Field(default=None, ge=-1, le=1)
    # A second model call's judgement of the hypothesis, when the check is on.
    verdict: Verdict | None = None
    verdict_reason: str | None = None
