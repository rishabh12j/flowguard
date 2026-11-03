from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator


class Incident(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", str_strip_whitespace=True)

    incident_id: str = Field(pattern=r"^\S+$")
    description: str = Field(min_length=1)
    affected_system: str = Field(pattern=r"^\S+$")
    start_time: AwareDatetime
    end_time: AwareDatetime

    @model_validator(mode="after")
    def window_is_in_order(self) -> "Incident":
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self
