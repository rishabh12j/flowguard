from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from flowguard.domain.redaction import redact


class Incident(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", str_strip_whitespace=True)

    incident_id: str = Field(pattern=r"^\S+$")
    description: str = Field(min_length=1)
    affected_system: str = Field(pattern=r"^\S+$")
    start_time: AwareDatetime
    end_time: AwareDatetime

    # A reporter may paste a log line with a credential in it. It would otherwise
    # reach the model, the checkpoint, and the audit record.
    @field_validator("description")
    @classmethod
    def without_credentials(cls, description: str) -> str:
        return redact(description)

    @model_validator(mode="after")
    def window_is_in_order(self) -> "Incident":
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self
