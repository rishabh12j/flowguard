import json
import sqlite3
import threading
from datetime import UTC, datetime

import pytest

from flowguard.domain.audit import (
    DuplicateVersion,
    InvestigationRecord,
    ToolCallRecord,
)
from flowguard.storage.audit_repository import SqliteAuditStore

STARTED = datetime(2026, 7, 15, 11, 5, tzinfo=UTC)


def record(
    investigation_id: str = "INVEST-1", version: int = 1, status: str = "abstained"
) -> InvestigationRecord:
    return InvestigationRecord(
        investigation_id=investigation_id,
        version=version,
        status=status,
        started_at=STARTED,
        finished_at=STARTED,
        incident=None,
        category="unknown",
        evidence_ids=("LOG-882",),
        tool_calls=(
            ToolCallRecord(
                tool="search_logs", arguments={}, outcome="ok", items=1, seconds=0.2
            ),
        ),
        hypotheses=(),
        selected_hypothesis_id=None,
        abstention="no evidence was gathered",
        errors=(),
    )


def test_a_saved_record_reads_back_unchanged():
    store = SqliteAuditStore()

    store.save(record())

    assert store.get("INVEST-1") == record()


def test_an_unknown_investigation_is_none():
    assert SqliteAuditStore().get("INVEST-404") is None


def test_a_version_cannot_be_saved_twice():
    store = SqliteAuditStore()
    store.save(record())

    with pytest.raises(DuplicateVersion, match="INVEST-1 version 1"):
        store.save(record(status="approved"))

    assert store.get("INVEST-1").status == "abstained"


def test_records_survive_reopening_the_file(tmp_path):
    path = tmp_path / "audit.db"
    SqliteAuditStore(path).save(record())

    assert SqliteAuditStore(path).get("INVEST-1") == record()


def test_can_save_from_another_thread():
    store = SqliteAuditStore()
    failures = []

    def save() -> None:
        try:
            store.save(record("INVEST-2"))
        except Exception as error:  # noqa: BLE001
            failures.append(error)

    thread = threading.Thread(target=save)
    thread.start()
    thread.join()

    assert failures == []
    assert store.get("INVEST-2") is not None


def test_threads_take_turns_with_the_connection():
    store = SqliteAuditStore()

    with store._lock:
        thread = threading.Thread(target=store.save, args=(record(),))
        thread.start()
        thread.join(timeout=0.2)
        # The save waits while another thread is using the connection.
        assert thread.is_alive()
    thread.join()

    assert store.get("INVEST-1") is not None


def test_every_version_is_kept_and_the_latest_is_read():
    store = SqliteAuditStore()
    first = record(status="awaiting_approval")
    second = record(version=2, status="approved")

    store.save(first)
    store.save(second)

    assert store.get("INVEST-1") == second
    assert store.history("INVEST-1") == [first, second]


def test_an_unknown_investigation_has_no_history():
    assert SqliteAuditStore().history("INVEST-404") == []


def test_records_saved_before_versions_become_version_1(tmp_path):
    path = tmp_path / "audit.db"
    old = json.loads(record().model_dump_json())
    del old["version"]
    with sqlite3.connect(path) as connection:
        connection.execute(
            "CREATE TABLE investigations (investigation_id TEXT PRIMARY KEY, "
            "incident_id TEXT, status TEXT NOT NULL, category TEXT, "
            "finished_at TEXT NOT NULL, record TEXT NOT NULL)"
        )
        connection.execute(
            "INSERT INTO investigations VALUES (?, ?, ?, ?, ?, ?)",
            (
                "INVEST-1",
                None,
                "abstained",
                "unknown",
                STARTED.isoformat(),
                json.dumps(old),
            ),
        )
    connection.close()

    SqliteAuditStore(path)
    store = SqliteAuditStore(path)

    assert store.history("INVEST-1") == [record()]
