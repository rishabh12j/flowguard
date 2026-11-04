import os
from dataclasses import dataclass
from pathlib import Path

AUDIT_DB_VARIABLE = "FLOWGUARD_AUDIT_DB"
DEFAULT_AUDIT_DB = Path("flowguard-audit.db")


@dataclass(frozen=True)
class Settings:
    audit_db: Path = DEFAULT_AUDIT_DB

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(audit_db=Path(os.environ.get(AUDIT_DB_VARIABLE, DEFAULT_AUDIT_DB)))
