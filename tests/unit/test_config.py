from pathlib import Path

from flowguard.config import AUDIT_DB_VARIABLE, CHECKPOINT_DB_VARIABLE, Settings


def test_the_audit_database_defaults_to_the_working_directory(monkeypatch):
    monkeypatch.delenv(AUDIT_DB_VARIABLE, raising=False)
    monkeypatch.delenv(CHECKPOINT_DB_VARIABLE, raising=False)

    settings = Settings.from_env()

    assert settings.audit_db == Path("flowguard-audit.db")
    assert settings.checkpoint_db == Path("flowguard-checkpoints.db")


def test_the_environment_chooses_the_audit_database(monkeypatch, tmp_path):
    monkeypatch.setenv(AUDIT_DB_VARIABLE, str(tmp_path / "audit.db"))

    assert Settings.from_env().audit_db == tmp_path / "audit.db"


def test_the_environment_chooses_the_checkpoint_database(monkeypatch, tmp_path):
    monkeypatch.setenv(CHECKPOINT_DB_VARIABLE, str(tmp_path / "checkpoints.db"))

    assert Settings.from_env().checkpoint_db == tmp_path / "checkpoints.db"
