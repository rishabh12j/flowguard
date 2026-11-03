from typing import Protocol

MODEL_NAME = "BAAI/bge-small-en-v1.5"


class Embedder(Protocol):
    dimensions: int
    max_tokens: int

    def count_tokens(self, text: str) -> int: ...

    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...

    def embed_query(self, text: str) -> list[float]: ...


class SentenceTransformerEmbedder:
    def __init__(self, model_name: str = MODEL_NAME) -> None:
        # Importing PyTorch takes seconds, so only load it when it's needed.
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(model_name)
        dimensions = self._model.get_embedding_dimension()
        if dimensions is None:
            raise ValueError(f"{model_name} does not report its dimensions")
        self.dimensions = dimensions
        self.max_tokens = self._model.max_seq_length

    def count_tokens(self, text: str) -> int:
        return len(self._model.tokenizer(text, truncation=False)["input_ids"])

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._model.encode_document(texts, normalize_embeddings=True).tolist()

    def embed_query(self, text: str) -> list[float]:
        return self._model.encode_query(text, normalize_embeddings=True).tolist()
