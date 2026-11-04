from pydantic import BaseModel, ConfigDict, Field, model_validator


class ProposedHypothesis(BaseModel):
    """A root cause suggested by the model, before code scores its confidence."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    description: str = Field(min_length=1)
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
