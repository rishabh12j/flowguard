import json

import httpx
import pytest

from flowguard.llm.client import OLLAMA_URL, LLMError, OllamaLLM

SCHEMA = {"type": "object"}


def llm_answering(handler) -> OllamaLLM:
    client = httpx.Client(base_url=OLLAMA_URL, transport=httpx.MockTransport(handler))
    # No waiting between retries, so the tests stay fast.
    return OllamaLLM(client=client, retry_delay_seconds=0)


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
    assert body["truncate"] is False
    assert body["options"]["temperature"] == 0.0
    assert body["messages"] == [
        {"role": "system", "content": "system"},
        {"role": "user", "content": "prompt"},
    ]


def test_a_reasoning_level_is_sent_for_models_that_cannot_turn_it_off():
    sent = []

    def handler(request):
        sent.append(json.loads(request.content))
        return reply("{}")

    client = httpx.Client(base_url=OLLAMA_URL, transport=httpx.MockTransport(handler))
    OllamaLLM("gpt-oss:20b", client=client, think="low").generate("s", "p", SCHEMA)

    assert (sent[0]["model"], sent[0]["think"]) == ("gpt-oss:20b", "low")


def test_a_missing_model_raises_llm_error():
    llm = llm_answering(
        lambda request: httpx.Response(
            404, json={"error": "model 'gemma4:12b' not found"}
        )
    )

    with pytest.raises(LLMError, match="not found"):
        llm.generate("system", "prompt", SCHEMA)


def test_a_prompt_too_long_for_the_context_raises_llm_error_once():
    # Ollama's answer when truncation is off, seen with 133 evidence items.
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(
            400,
            json={
                "error": "request (12677 tokens) exceeds the available context "
                "size (8192 tokens), try increasing it"
            },
        )

    with pytest.raises(LLMError, match="exceeds the available context"):
        llm_answering(handler).generate("system", "prompt", SCHEMA)
    assert len(calls) == 1


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


def answers_in_turn(*responses):
    """A handler that gives each response once, in order, and counts the calls."""
    calls = []

    def handler(request):
        response = responses[len(calls)]
        calls.append(request)
        if isinstance(response, Exception):
            raise response
        return response

    return handler, calls


def test_a_crashed_runner_is_retried():
    handler, calls = answers_in_turn(
        httpx.Response(500, json={"error": "llama-server process has terminated"}),
        reply('{"ok": true}'),
    )

    assert llm_answering(handler).generate("system", "prompt", SCHEMA) == '{"ok": true}'
    assert len(calls) == 2


def test_a_lost_connection_is_retried():
    handler, calls = answers_in_turn(httpx.ConnectError("refused"), reply("{}"))

    llm_answering(handler).generate("system", "prompt", SCHEMA)

    assert len(calls) == 2


def test_retries_stop_after_the_limit():
    handler, calls = answers_in_turn(*[httpx.Response(503) for _ in range(5)])

    with pytest.raises(LLMError, match="failed with 503"):
        llm_answering(handler).generate("system", "prompt", SCHEMA)

    assert len(calls) == 3


@pytest.mark.parametrize(
    "response",
    [
        httpx.Response(404, json={"error": "model 'gemma4:12b' not found"}),
        httpx.ReadTimeout("too slow"),
    ],
)
def test_lasting_failures_and_timeouts_are_not_retried(response):
    handler, calls = answers_in_turn(response, reply("{}"))

    with pytest.raises(LLMError):
        llm_answering(handler).generate("system", "prompt", SCHEMA)

    assert len(calls) == 1


def test_each_retry_waits_longer(monkeypatch):
    waits = []
    monkeypatch.setattr("flowguard.llm.client.time.sleep", waits.append)
    handler, _ = answers_in_turn(*[httpx.Response(500) for _ in range(3)])
    client = httpx.Client(base_url=OLLAMA_URL, transport=httpx.MockTransport(handler))

    with pytest.raises(LLMError):
        OllamaLLM(client=client, retry_delay_seconds=2).generate("s", "p", SCHEMA)

    assert waits == [2, 4]


def test_the_ollama_address_can_be_chosen():
    llm = OllamaLLM(base_url="http://ollama:11434")

    assert str(llm._client.base_url) == "http://ollama:11434"
