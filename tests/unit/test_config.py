from pathlib import Path

from flowguard.config import (
    AUDIT_DB_VARIABLE,
    CHECKPOINT_DB_VARIABLE,
    MODEL_VARIABLE,
    OLLAMA_URL_VARIABLE,
    QDRANT_URL_VARIABLE,
    Settings,
)


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


def test_ollama_and_qdrant_default_to_this_computer_and_memory(monkeypatch):
    for variable in (OLLAMA_URL_VARIABLE, MODEL_VARIABLE, QDRANT_URL_VARIABLE):
        monkeypatch.delenv(variable, raising=False)

    settings = Settings.from_env()

    assert settings.ollama_url == "http://localhost:11434"
    assert settings.model == "gemma4:12b"
    assert settings.qdrant_url is None


def test_the_environment_chooses_ollama_the_model_and_qdrant(monkeypatch):
    monkeypatch.setenv(OLLAMA_URL_VARIABLE, "http://ollama:11434")
    monkeypatch.setenv(MODEL_VARIABLE, "gemma4:e4b")
    monkeypatch.setenv(QDRANT_URL_VARIABLE, "http://qdrant:6333")

    settings = Settings.from_env()

    assert (settings.ollama_url, settings.model, settings.qdrant_url) == (
        "http://ollama:11434",
        "gemma4:e4b",
        "http://qdrant:6333",
    )


def test_an_empty_qdrant_url_means_memory(monkeypatch):
    monkeypatch.setenv(QDRANT_URL_VARIABLE, "")

    assert Settings.from_env().qdrant_url is None
