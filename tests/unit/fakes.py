import hashlib
import json


class FakeEmbedder:
    """Gives repeatable vectors without loading a real model."""

    dimensions = 4
    max_tokens = 1000

    def count_tokens(self, text: str) -> int:
        return len(text.split())

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_query(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode()).digest()
        return [byte / 255 + 0.01 for byte in digest[:4]]


class FakeLLM:
    """Returns a fixed answer, or raises a fixed error, and records every request."""

    def __init__(
        self,
        *hypotheses: dict,
        answer: str | None = None,
        error: Exception | None = None,
    ) -> None:
        self.answer = answer or json.dumps({"hypotheses": list(hypotheses)})
        self.error = error
        self.calls: list[tuple[str, str, dict]] = []

    def generate(self, system: str, prompt: str, schema: dict) -> str:
        self.calls.append((system, prompt, schema))
        if self.error is not None:
            raise self.error
        return self.answer
