import pytest

from flowguard.dataset import load_evidence, load_incident
from flowguard.domain.evidence import EvidenceItem
from flowguard.domain.redaction import redact, redact_evidence


@pytest.mark.parametrize(
    "text, expected",
    [
        (
            "login failed: password=hunter2 for user sam",
            "login failed: password=[REDACTED] for user sam",
        ),
        (
            'config {"api_key": "sk-live-123abc", "region": "eu"}',
            'config {"api_key": "[REDACTED]", "region": "eu"}',
        ),
        ("client_secret = 'zzz'", "client_secret = '[REDACTED]'"),
        ("Authorization: Bearer abc.def-ghi_jkl==", "Authorization: Bearer [REDACTED]"),
        (
            "jwt eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.c2lnbmF0dXJl ok",
            "jwt [REDACTED] ok",
        ),
        ("key AKIAABCDEFGHIJKLMNOP used", "key [REDACTED] used"),
        (
            "postgres://svc:S3cret!@db.internal:5432/invoices",
            "postgres://svc:[REDACTED]@db.internal:5432/invoices",
        ),
        (
            "-----BEGIN RSA PRIVATE KEY-----\nMIIabc\n-----END RSA PRIVATE KEY----- after",
            "[REDACTED] after",
        ),
    ],
)
def test_credentials_are_replaced(text, expected):
    assert redact(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "token expired at 09:43; retrying with a new token",
        "required field supplier_id is missing",
        "https://api.example.com/v3/invoices",
    ],
)
def test_ordinary_text_is_left_alone(text):
    assert redact(text) == text


def test_redacting_twice_changes_nothing_more():
    once = redact("password=hunter2 and Bearer abc")

    assert redact(once) == once


def test_evidence_is_redacted_in_title_content_and_metadata():
    item = EvidenceItem(
        evidence_id="LOG-900",
        source_type="log",
        source_name="erp-connector",
        title="Retry with password=hunter2",
        content="Authorization: Bearer abc123",
        metadata={
            "headers": {"Authorization": "Basic c2FtOmh1bnRlcjI="},
            "attempts": [{"note": "api_key=sk-1"}],
            "level": "WARN",
        },
    )

    redacted = redact_evidence(item)

    assert redacted.title == "Retry with password=[REDACTED]"
    assert redacted.content == "Authorization: Bearer [REDACTED]"
    assert redacted.metadata == {
        "headers": {"Authorization": "[REDACTED]"},
        "attempts": [{"note": "api_key=[REDACTED]"}],
        "level": "WARN",
    }
    assert "hunter2" not in redacted.model_dump_json()


def test_the_seeded_data_holds_no_credentials():
    # If this fails, a seeded file gained something that looks like a credential.
    assert [item for item in load_evidence() if redact_evidence(item) != item] == []
    description = load_incident("INC-001")["description"]
    assert redact(description) == description
