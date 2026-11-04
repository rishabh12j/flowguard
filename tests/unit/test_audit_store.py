import sqlite3
import threading
from datetime import UTC, datetime

import pytest

from flowguard.domain.audit import InvestigationRecord, ToolCallRecord
from flowguard.storage.audit_repository import SqliteAuditStore

STARTED = datetime(2026, 7, 15, 11, 5, tzinfo=UTC)


def record(investigation_id: str = "INVEST-1") -> InvestigationRecord:
    return InvestigationRecord(
        investigation_id=investigation_id,
        status="abstained",
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


def test_a_record_cannot_be_saved_twice():
    store = SqliteAuditStore()
    store.save(record())

    with pytest.raises(sqlite3.IntegrityError):
        store.save(record())


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
