from pathlib import Path

from flowguard.config import AUDIT_DB_VARIABLE, Settings


def test_the_audit_database_defaults_to_the_working_directory(monkeypatch):
    monkeypatch.delenv(AUDIT_DB_VARIABLE, raising=False)

    assert Settings.from_env().audit_db == Path("flowguard-audit.db")


def test_the_environment_chooses_the_audit_database(monkeypatch, tmp_path):
    monkeypatch.setenv(AUDIT_DB_VARIABLE, str(tmp_path / "audit.db"))

    assert Settings.from_env().audit_db == tmp_path / "audit.db"
