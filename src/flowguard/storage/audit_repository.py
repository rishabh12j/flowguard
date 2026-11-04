import sqlite3
import threading
from pathlib import Path

from flowguard.domain.audit import DuplicateVersion, InvestigationRecord

SCHEMA = """
CREATE TABLE IF NOT EXISTS investigation_versions (
    investigation_id TEXT NOT NULL,
    version INTEGER NOT NULL,
    incident_id TEXT,
    status TEXT NOT NULL,
    category TEXT,
    saved_at TEXT NOT NULL,
    record TEXT NOT NULL,
    PRIMARY KEY (investigation_id, version)
)
"""
# Records saved before versions existed become version 1. OR IGNORE makes this
# safe to run every time the store opens.
MIGRATE_UNVERSIONED = """
INSERT OR IGNORE INTO investigation_versions
SELECT investigation_id, 1, incident_id, status, category, finished_at, record
FROM investigations
"""


class SqliteAuditStore:
    """Keeps every version of every investigation record. Nothing is ever changed."""

    def __init__(self, path: str | Path = ":memory:") -> None:
        # The audit node runs in a worker thread, not the thread that opened this.
        self._connection = sqlite3.connect(path, check_same_thread=False)
        # Requests run in several threads at once, and they share this one
        # connection. A rollback in one thread would undo another thread's
        # unsaved insert, so only one thread uses the connection at a time.
        self._lock = threading.Lock()
        with self._connection:
            self._connection.execute(SCHEMA)
            if self._has_table("investigations"):
                self._connection.execute(MIGRATE_UNVERSIONED)

    def _has_table(self, name: str) -> bool:
        row = self._connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?", (name,)
        ).fetchone()
        return row is not None

    def save(self, record: InvestigationRecord) -> None:
        # A plain INSERT, so each version can be saved only once. Two decisions
        # racing to save the same version can't both succeed.
        try:
            with self._lock, self._connection:
                self._connection.execute(
                    "INSERT INTO investigation_versions VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        record.investigation_id,
                        record.version,
                        record.incident.incident_id if record.incident else None,
                        record.status,
                        record.category,
                        record.finished_at.isoformat(),
                        record.model_dump_json(),
                    ),
                )
        except sqlite3.IntegrityError as error:
            raise DuplicateVersion(
                f"{record.investigation_id} version {record.version} is already saved"
            ) from error

    def get(self, investigation_id: str) -> InvestigationRecord | None:
        """The latest version of an investigation's record."""
        versions = self._select(
            "SELECT record FROM investigation_versions WHERE investigation_id = ? "
            "ORDER BY version DESC LIMIT 1",
            investigation_id,
        )
        return versions[0] if versions else None

    def history(self, investigation_id: str) -> list[InvestigationRecord]:
        """Every version of an investigation's record, oldest first."""
        return self._select(
            "SELECT record FROM investigation_versions WHERE investigation_id = ? "
            "ORDER BY version",
            investigation_id,
        )

    def _select(self, query: str, investigation_id: str) -> list[InvestigationRecord]:
        with self._lock:
            rows = self._connection.execute(query, (investigation_id,)).fetchall()
        return [InvestigationRecord.model_validate_json(row[0]) for row in rows]
