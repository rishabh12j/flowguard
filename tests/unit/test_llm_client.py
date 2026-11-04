import json

import httpx
import pytest

from flowguard.llm.client import OLLAMA_URL, LLMError, OllamaLLM

SCHEMA = {"type": "object"}


def llm_answering(handler) -> OllamaLLM:
    client = httpx.Client(base_url=OLLAMA_URL, transport=httpx.MockTransport(handler))
    return OllamaLLM(client=client)


def reply(content: str) -> httpx.Response:
    return httpx.Response(
        200, json={"message": {"role": "assistant", "content": content}}
    )


def test_returns_the_message_content():
    llm = llm_answering(lambda request: reply('{"ok": true}'))

    assert llm.generate("system", "prompt", SCHEMA) == '{"ok": true}'


def test_sends_the_schema_with_thinking_and_streaming_off():
    sent = []

    def handler(request):
        sent.append(json.loads(request.content))
        return reply("{}")

    llm_answering(handler).generate("system", "prompt", SCHEMA)

    body = sent[0]
    assert body["model"] == "gemma4:12b"
    assert body["format"] == SCHEMA
    assert body["think"] is False
    assert body["stream"] is False
    assert body["options"]["temperature"] == 0.0
    assert body["messages"] == [
        {"role": "system", "content": "system"},
        {"role": "user", "content": "prompt"},
    ]


def test_a_missing_model_raises_llm_error():
    llm = llm_answering(
        lambda request: httpx.Response(
            404, json={"error": "model 'gemma4:12b' not found"}
        )
    )

    with pytest.raises(LLMError, match="not found"):
        llm.generate("system", "prompt", SCHEMA)


@pytest.mark.parametrize(
    ("problem", "message"),
    [
        (httpx.ConnectError("connection refused"), "could not reach Ollama"),
        (httpx.ReadTimeout("too slow"), "did not answer in time"),
    ],
)
def test_connection_problems_raise_llm_error(problem, message):
    def handler(request):
        raise problem

    with pytest.raises(LLMError, match=message):
        llm_answering(handler).generate("system", "prompt", SCHEMA)


def test_a_reply_without_a_message_raises_llm_error():
    llm = llm_answering(lambda request: httpx.Response(200, json={"done": True}))

    with pytest.raises(LLMError, match="no message"):
        llm.generate("system", "prompt", SCHEMA)
