from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator

Decision = Literal["approve", "reject", "request_more_evidence"]


class ApprovalDecision(BaseModel):
    """A person's decision on a plan that needs approval."""

    model_config = ConfigDict(frozen=True, extra="forbid", str_strip_whitespace=True)

    decision: Decision
    approver: str = Field(min_length=1, max_length=100)
    comment: str = Field(default="", max_length=2000)
    decided_at: AwareDatetime

    @model_validator(mode="after")
    def a_refusal_says_why(self) -> "ApprovalDecision":
        if self.decision != "approve" and not self.comment:
            raise ValueError(f"{self.decision} needs a comment saying why")
        return self
