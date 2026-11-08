import time
from typing import Any, Literal, Protocol

import httpx

MODEL = "gemma4:12b"
OLLAMA_URL = "http://localhost:11434"

# Ollama's reasoning setting. False turns it off. gpt-oss ignores False and
# reasons at its default level, so it needs "low" to be as close to off as it gets.
Think = bool | Literal["low", "medium", "high"]


class LLMError(Exception):
    """The model could not produce a response."""


class ModelDeclined(LLMError):
    """The model chose not to answer, such as a safety refusal.

    It's the model's answer, not an outage: FlowGuard abstains, and an
    evaluation scores it instead of stopping.
    """


class TransientLLMError(LLMError):
    """A failure that may not happen again, such as a crashed model runner."""


class LLM(Protocol):
    def generate(self, system: str, prompt: str, schema: dict[str, Any]) -> str: ...


class OllamaLLM:
    def __init__(
        self,
        model: str = MODEL,
        *,
        client: httpx.Client | None = None,
        base_url: str = OLLAMA_URL,
        temperature: float = 0.0,
        think: Think = False,
        timeout_seconds: float = 300.0,
        retries: int = 2,
        retry_delay_seconds: float = 2.0,
    ) -> None:
        self.model = model
        self.temperature = temperature
        self.think = think
        self.retries = retries
        self.retry_delay_seconds = retry_delay_seconds
        # The first call loads the model into memory, which took nearly three minutes in testing.
        self._client = client or httpx.Client(
            base_url=base_url, timeout=timeout_seconds
        )

    def generate(self, system: str, prompt: str, schema: dict[str, Any]) -> str:
        # Only transient failures are retried, a fixed number of times, waiting
        # longer each time. Ollama's runner sometimes crashes and restarts.
        for attempt in range(self.retries + 1):
            try:
                return self._generate_once(system, prompt, schema)
            except TransientLLMError:
                if attempt == self.retries:
                    raise
                time.sleep(self.retry_delay_seconds * 2**attempt)
        raise AssertionError("unreachable: the last attempt returns or raises")

    def _generate_once(self, system: str, prompt: str, schema: dict[str, Any]) -> str:
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
                    # A prompt longer than the context would otherwise be cut from
                    # the front, losing the instructions without an error.
                    "truncate": False,
                    "think": self.think,
                    "options": {"temperature": self.temperature, "num_ctx": 8192},
                },
            )
        except httpx.TimeoutException as error:
            # Not retried: Ollama may still be generating, and a retry would queue
            # a second request behind it.
            raise LLMError(f"{self.model} did not answer in time") from error
        except httpx.TransportError as error:
            raise TransientLLMError(f"could not reach Ollama: {error}") from error

        if response.is_server_error:
            raise TransientLLMError(
                f"{self.model} failed with {response.status_code}: {response.text[:200]}"
            )
        # A client error, such as a missing model, won't fix itself.
        if response.is_error:
            raise LLMError(
                f"{self.model} failed with {response.status_code}: {response.text[:200]}"
            )
        content = response.json().get("message", {}).get("content")
        if not isinstance(content, str):
            raise LLMError(f"{self.model} returned no message")
        return content
