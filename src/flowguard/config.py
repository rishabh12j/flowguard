import os
from dataclasses import dataclass
from pathlib import Path

from flowguard.llm.client import MODEL, OLLAMA_URL

AUDIT_DB_VARIABLE = "FLOWGUARD_AUDIT_DB"
DEFAULT_AUDIT_DB = Path("flowguard-audit.db")
CHECKPOINT_DB_VARIABLE = "FLOWGUARD_CHECKPOINT_DB"
DEFAULT_CHECKPOINT_DB = Path("flowguard-checkpoints.db")
OLLAMA_URL_VARIABLE = "FLOWGUARD_OLLAMA_URL"
MODEL_VARIABLE = "FLOWGUARD_MODEL"
QDRANT_URL_VARIABLE = "FLOWGUARD_QDRANT_URL"


@dataclass(frozen=True)
class Settings:
    audit_db: Path = DEFAULT_AUDIT_DB
    checkpoint_db: Path = DEFAULT_CHECKPOINT_DB
    ollama_url: str = OLLAMA_URL
    model: str = MODEL
    # None keeps the document index in memory, rebuilt at every start.
    qdrant_url: str | None = None

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            audit_db=Path(os.environ.get(AUDIT_DB_VARIABLE, DEFAULT_AUDIT_DB)),
            checkpoint_db=Path(
                os.environ.get(CHECKPOINT_DB_VARIABLE, DEFAULT_CHECKPOINT_DB)
            ),
            ollama_url=os.environ.get(OLLAMA_URL_VARIABLE, OLLAMA_URL),
            model=os.environ.get(MODEL_VARIABLE, MODEL),
            qdrant_url=os.environ.get(QDRANT_URL_VARIABLE) or None,
        )
