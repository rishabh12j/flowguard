import re
from typing import Any

from flowguard.domain.evidence import EvidenceItem

REDACTED = "[REDACTED]"

# Each pattern keeps its first group, if it has one, and replaces the rest. The
# patterns look for a credential's shape, so ordinary words like "token expired"
# are left alone.
PATTERNS = (
    # A whole private key, across lines.
    re.compile(
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----",
        re.DOTALL,
    ),
    # Authorization: Bearer <token>
    re.compile(r"(?i)(\bbearer\s+)[A-Za-z0-9._~+/-]+=*"),
    # A JSON Web Token: three base64url parts, the first starting with eyJ.
    re.compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"),
    # An AWS access key ID.
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    # The password in scheme://user:password@host.
    re.compile(r"(\b[a-z][a-z0-9+.-]*://[^\s:/@]+:)[^\s@/]+(?=@)"),
    # password=..., api_key: ..., client_secret="...", and similar.
    re.compile(
        r"(?i)(\b(?:password|passwd|pwd|secret|client[_-]?secret|api[_-]?key"
        r"|access[_-]?key|auth[_-]?token|access[_-]?token|token)\b[\"']?\s*[:=]\s*[\"']?)"
        r"[^\s\"',;]+"
    ),
)
# Metadata keys whose values are always secret, whatever they look like.
SECRET_KEYS = re.compile(r"(?i)password|passwd|secret|api[_-]?key|token|authorization")


def redact(text: str) -> str:
    for pattern in PATTERNS:
        text = pattern.sub(
            lambda match: (match.group(1) if pattern.groups else "") + REDACTED, text
        )
    return text


def redact_value(key: str, value: Any) -> Any:
    if isinstance(value, str):
        return REDACTED if SECRET_KEYS.search(key) else redact(value)
    if isinstance(value, dict):
        return {name: redact_value(name, inner) for name, inner in value.items()}
    if isinstance(value, list):
        return [redact_value(key, inner) for inner in value]
    return value


def redact_evidence(item: EvidenceItem) -> EvidenceItem:
    """The same evidence with every credential replaced by [REDACTED]."""
    return item.model_copy(
        update={
            "title": redact(item.title),
            "content": redact(item.content),
            "metadata": redact_value("", item.metadata),
        }
    )
