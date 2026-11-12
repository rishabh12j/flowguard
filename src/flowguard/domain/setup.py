"""What one production setup records, declared once per setup.

Setups differ in what they keep. Most record deployments; fewer record
configuration changes, feature flags or migrations. So when FlowGuard finds no
change that explains a failure, that means "nothing changed" only for the kinds of
change the setup records. The profile says which those are, and the decision rules
read it (graph/nodes/explain.py).

A data folder states its profile in setup.json; without one, every kind is taken
as recorded, which is what the benchmarks built before 2026-11-12 assume.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict

ChangeKind = Literal["deployment", "configuration", "feature_flag", "migration"]
CHANGE_KINDS: tuple[ChangeKind, ...] = (
    "deployment",
    "configuration",
    "feature_flag",
    "migration",
)


class SetupProfile(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    recorded_changes: tuple[ChangeKind, ...] = CHANGE_KINDS

    @property
    def unrecorded(self) -> tuple[ChangeKind, ...]:
        return tuple(k for k in CHANGE_KINDS if k not in self.recorded_changes)
