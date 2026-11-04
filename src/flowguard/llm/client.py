from typing import Any, Protocol

import httpx

MODEL = "gemma4:12b"
OLLAMA_URL = "http://localhost:11434"


class LLMError(Exception):
    """The model could not produce a response."""


class LLM(Protocol):
    def generate(self, system: str, prompt: str, schema: dict[str, Any]) -> str: ...


class OllamaLLM:
    def __init__(
        self,
        model: str = MODEL,
        *,
        client: httpx.Client | None = None,
        temperature: float = 0.0,
        timeout_seconds: float = 300.0,
    ) -> None:
        self.model = model
        self.temperature = temperature
        # The first call loads the model into memory, which took nearly three minutes in testing.
        self._client = client or httpx.Client(
            base_url=OLLAMA_URL, timeout=timeout_seconds
        )

    def generate(self, system: str, prompt: str, schema: dict[str, Any]) -> str:
        try:
            response = self._client.post(
                "/api/chat",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ],
                    # Ollama only lets the model produce text that matches this schema.
                    "format": schema,
                    "stream": False,
                    "think": False,
                    "options": {"temperature": self.temperature, "num_ctx": 8192},
                },
            )
        except httpx.TimeoutException as error:
            # Giving up here does not stop Ollama, which may keep generating.
            raise LLMError(f"{self.model} did not answer in time") from error
        except httpx.TransportError as error:
            raise LLMError(f"could not reach Ollama: {error}") from error

        if response.is_error:
            raise LLMError(
                f"{self.model} failed with {response.status_code}: {response.text[:200]}"
            )
        content = response.json().get("message", {}).get("content")
        if not isinstance(content, str):
            raise LLMError(f"{self.model} returned no message")
        return content
