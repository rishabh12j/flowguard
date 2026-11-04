import sqlite3
from pathlib import Path

from flowguard.domain.audit import InvestigationRecord

SCHEMA = """
CREATE TABLE IF NOT EXISTS investigations (
    investigation_id TEXT PRIMARY KEY,
    incident_id TEXT,
    status TEXT NOT NULL,
    category TEXT,
    finished_at TEXT NOT NULL,
    record TEXT NOT NULL
)
"""


class SqliteAuditStore:
    """Keeps investigation records. Records are only ever added, never changed."""

    def __init__(self, path: str | Path = ":memory:") -> None:
        # The audit node runs in a worker thread, not the thread that opened this.
        self._connection = sqlite3.connect(path, check_same_thread=False)
        with self._connection:
            self._connection.execute(SCHEMA)

    def save(self, record: InvestigationRecord) -> None:
        # A plain INSERT, so saving the same investigation twice fails.
        with self._connection:
            self._connection.execute(
                "INSERT INTO investigations VALUES (?, ?, ?, ?, ?, ?)",
                (
                    record.investigation_id,
                    record.incident.incident_id if record.incident else None,
                    record.status,
                    record.category,
                    record.finished_at.isoformat(),
                    record.model_dump_json(),
                ),
            )

    def get(self, investigation_id: str) -> InvestigationRecord | None:
        row = self._connection.execute(
            "SELECT record FROM investigations WHERE investigation_id = ?",
            (investigation_id,),
        ).fetchone()
        return InvestigationRecord.model_validate_json(row[0]) if row else None
