import hashlib


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
