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
        actions: list[dict] | None = None,
        later_actions: list[dict] | None = None,
        answer: str | None = None,
        error: Exception | None = None,
    ) -> None:
        self.answer = answer or json.dumps({"hypotheses": list(hypotheses)})
        self.actions = actions
        # The plan for every remediation question after the first, if different.
        self.later_actions = later_actions
        self.plans_given = 0
        self.error = error
        self.calls: list[tuple[str, str, dict]] = []

    def generate(self, system: str, prompt: str, schema: dict) -> str:
        self.calls.append((system, prompt, schema))
        if self.error is not None:
            raise self.error
        # The remediation schema asks for actions, so those questions get actions.
        if self.actions is not None and "actions" in schema.get("properties", {}):
            self.plans_given += 1
            later = self.plans_given > 1 and self.later_actions is not None
            return json.dumps(
                {"actions": self.later_actions if later else self.actions}
            )
        return self.answer
