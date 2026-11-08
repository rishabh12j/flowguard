from types import SimpleNamespace

import httpx
import pytest

anthropic = pytest.importorskip("anthropic")

from flowguard.evaluation.investigations import ModelUnavailable, Watched  # noqa: E402
from flowguard.graph.nodes.root_cause import proposal_schema  # noqa: E402
from flowguard.llm.claude import ClaudeLLM, claude_schema  # noqa: E402
from flowguard.llm.client import LLMError, ModelDeclined  # noqa: E402


def response(text="{}", stop_reason="end_turn", category=None):
    return SimpleNamespace(
        content=[
            SimpleNamespace(type="thinking", thinking=""),
            SimpleNamespace(type="text", text=text),
        ],
        stop_reason=stop_reason,
        stop_details=SimpleNamespace(category=category) if category else None,
        usage=SimpleNamespace(input_tokens=100, output_tokens=20),
    )


class FakeMessages:
    def __init__(self, result):
        self.result = result
        self.sent = []

    def create(self, **request):
        self.sent.append(request)
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


def claude(result, **options):
    messages = FakeMessages(result)
    llm = ClaudeLLM(client=SimpleNamespace(messages=messages), **options)
    return llm, messages


def test_returns_the_text_and_counts_tokens():
    llm, _ = claude(response('{"ok": true}'))

    assert llm.generate("system", "prompt", {"type": "object"}) == '{"ok": true}'
    assert (llm.input_tokens, llm.output_tokens) == (100, 20)


def test_thinking_is_off_by_default_and_the_schema_is_sent():
    llm, messages = claude(response())

    llm.generate("system", "prompt", {"type": "object"})

    request = messages.sent[0]
    assert request["model"] == "claude-sonnet-5-5"
    assert request["system"] == "system"
    assert request["messages"] == [{"role": "user", "content": "prompt"}]
    assert request["thinking"] == {"type": "between_tools"}
    assert request["output_config"] == {
        "format": {"type": "json_schema", "schema": {"type": "object"}}
    }
    # Sonnet 5.5 rejects sampling settings, so none is sent.
    assert "temperature" not in request


def test_an_effort_turns_adaptive_thinking_on():
    llm, messages = claude(response(), effort="low")

    llm.generate("system", "prompt", {"type": "object"})

    assert messages.sent[0]["thinking"] == {"type": "adaptive"}
    assert messages.sent[0]["output_config"]["effort"] == "low"


def test_unsupported_constraints_are_dropped_but_enums_kept():
    schema = claude_schema(proposal_schema(["LOG-1", "LOG-2"]))
    text = str(schema)

    for keyword in ("minLength", "maxItems", "'minItems': 2"):
        assert keyword not in text
    hypothesis = schema["$defs"]["ProposedHypothesis"]["properties"]
    assert hypothesis["supporting_evidence_ids"]["items"]["enum"] == ["LOG-1", "LOG-2"]
    assert hypothesis["supporting_evidence_ids"]["minItems"] == 1
    assert schema["additionalProperties"] is False


def test_the_original_schema_is_not_changed():
    schema = proposal_schema(["LOG-1"])

    claude_schema(schema)

    assert schema["properties"]["hypotheses"]["minItems"] == 2


def test_a_refusal_is_the_models_answer_not_an_outage():
    llm, _ = claude(response("", stop_reason="refusal", category="cyber"))

    with pytest.raises(ModelDeclined, match="cyber"):
        Watched(llm).generate("system", "prompt", {"type": "object"})


def test_an_api_error_stops_an_evaluation():
    request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    error = anthropic.AuthenticationError(
        "invalid x-api-key", response=httpx.Response(401, request=request), body=None
    )
    llm, _ = claude(error)

    with pytest.raises(LLMError, match="401"):
        llm.generate("system", "prompt", {"type": "object"})
    with pytest.raises(ModelUnavailable):
        Watched(llm).generate("system", "prompt", {"type": "object"})
