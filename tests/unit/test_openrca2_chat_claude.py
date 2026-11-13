"""The Claude conversation of the baseline agent, against a fake transport: no request leaves."""

import json
from pathlib import Path
from typing import Any

import pytest

anthropic = pytest.importorskip("anthropic")
httpx2 = pytest.importorskip("httpx2")

from flowguard.openrca2.chat import ModelFailed, ToolSpec  # noqa: E402
from flowguard.openrca2.chat_claude import (  # noqa: E402
    BINDING_BETA,
    ClaudeConversation,
    without_thinking,
)

TOOL = ToolSpec(
    "think_tool",
    "note",
    {"type": "object", "properties": {"reflection": {"type": "string"}}},
)
USAGE = {
    "input_tokens": 10,
    "output_tokens": 5,
    "cache_creation_input_tokens": 0,
    "cache_read_input_tokens": 0,
}


def reply(
    content: list[dict[str, Any]], stop: str = "tool_use", **extra: Any
) -> dict[str, Any]:
    return {"id": "msg", "type": "message", "role": "assistant", "model": "claude-sonnet-5-5", "content": content,
            "stop_reason": stop, "stop_sequence": None, "usage": USAGE, **extra}  # fmt: skip


class Fake:
    def __init__(self, replies: list[Any]) -> None:
        self.replies = replies
        self.requests: list[httpx2.Request] = []

    def __call__(self, request: httpx2.Request) -> httpx2.Response:
        self.requests.append(request)
        item = self.replies.pop(0)
        return (
            item
            if isinstance(item, httpx2.Response)
            else httpx2.Response(200, json=item)
        )

    def body(self, i: int) -> dict[str, Any]:
        return json.loads(self.requests[i].content)


def conversation(fake: Fake, **kwargs: Any) -> ClaudeConversation:
    client = anthropic.Anthropic(
        api_key="x",
        max_retries=0,
        http_client=anthropic.DefaultHttpxClient(transport=httpx2.MockTransport(fake)),
    )
    return ClaudeConversation(
        "claude-sonnet-5-5", "investigate", "incident", [TOOL], client=client, **kwargs
    )


TURN = [
    {
        "type": "thinking",
        "thinking": "",
        "signature": "s1",
        "a_field_the_sdk_may_not_know": {"x": 1},
    },
    {
        "type": "tool_use",
        "id": "t1",
        "name": "think_tool",
        "input": {"reflection": "A → B ≥ 2×"},
        "caller": {"type": "direct"},
    },
    {"type": "thinking", "thinking": "", "signature": "s2"},
    {"type": "text", "text": "noted", "citations": None},
]


def test_a_turn_is_sent_back_exactly_as_it_came() -> None:
    fake = Fake(
        [
            reply(TURN),
            reply([{"type": "text", "text": "done", "citations": None}], "end_turn"),
        ]
    )
    convo = conversation(fake)
    first = convo.ask()
    assert [c.name for c in first.calls] == ["think_tool"] and first.calls[
        0
    ].arguments == {"reflection": "A → B ≥ 2×"}
    convo.answer_tools([(first.calls[0], "Reflection recorded")])
    convo.ask()
    assert fake.body(1)["messages"][1] == {"role": "assistant", "content": TURN}
    assert (
        fake.body(1)["system"] == fake.body(0)["system"]
        and fake.body(1)["tools"] == fake.body(0)["tools"]
    )


def test_the_answer_turn_replays_no_thinking_and_keeps_the_rest() -> None:
    fake = Fake(
        [
            reply(TURN),
            reply([{"type": "text", "text": "{}", "citations": None}], "end_turn"),
        ]
    )
    convo = conversation(fake)
    turn = convo.ask()
    convo.answer_tools([(turn.calls[0], "ok")])
    convo.conclude("synthesize", "answer now")
    body = fake.body(1)
    assert body["system"] == "synthesize" and body["tool_choice"] == {"type": "none"}
    sent = [
        b["type"]
        for m in body["messages"]
        if isinstance(m["content"], list)
        for b in m["content"]
    ]
    assert "thinking" not in sent and "tool_use" in sent and "tool_result" in sent
    assert convo.messages[1]["content"] == TURN  # the kept history is untouched


def test_without_thinking_drops_a_turn_that_was_only_thinking() -> None:
    messages = [
        {"role": "user", "content": "q"},
        {"role": "assistant", "content": [{"type": "redacted_thinking", "data": "x"}]},
    ]
    assert without_thinking(messages) == [{"role": "user", "content": "q"}]


def test_the_binding_controls_are_sent_and_their_report_recorded() -> None:
    report = [
        {
            "type": "thinking_dropped",
            "reason": "prefix_binding_mismatch",
            "path": "messages.1.content.2",
        }
    ]
    fake = Fake(
        [
            reply(
                [{"type": "text", "text": "x", "citations": None}],
                "end_turn",
                input_transformations=report,
            )
        ]
    )
    turn = conversation(fake, binding="drop_block").ask()
    assert BINDING_BETA in fake.requests[0].headers["anthropic-beta"]
    assert fake.body(0)["thinking"] == {
        "type": "adaptive",
        "block_binding": {"prefix_mismatch_behavior": "drop_block"},
    }
    assert turn.notes == [
        "input_transformation thinking_dropped: prefix_binding_mismatch at messages.1.content.2"
    ]


def test_no_binding_sends_no_thinking_field() -> None:
    fake = Fake([reply([{"type": "text", "text": "x", "citations": None}], "end_turn")])
    conversation(fake).ask()
    assert (
        "thinking" not in fake.body(0)
        and "anthropic-beta" not in fake.requests[0].headers
    )


def test_an_error_keeps_its_whole_message_and_the_diagnosis_header() -> None:
    message = (
        "messages.1.content.8: Invalid `signature` in `thinking` block. "
        + "x" * 400
        + " The first message that changed is messages.0."
    )
    error = httpx2.Response(
        400,
        json={
            "type": "error",
            "error": {"type": "invalid_request_error", "message": message},
        },
        headers={
            "anthropic-thinking-prefix-mismatch": "kind=blocks_modified; pattern=reserialized"
        },
    )
    with pytest.raises(ModelFailed) as failed:
        conversation(Fake([error])).ask()
    assert "The first message that changed is messages.0." in str(failed.value)
    assert "pattern=reserialized" in str(failed.value)


def test_requests_are_captured_and_spending_counted(tmp_path: Path) -> None:
    usage = {**USAGE, "input_tokens": 1_000_000}
    fake = Fake(
        [
            {
                **reply([{"type": "text", "text": "x", "citations": None}], "end_turn"),
                "usage": usage,
            }
        ]
    )
    convo = conversation(fake, capture=tmp_path / "case.jsonl")
    convo.ask()
    lines = (tmp_path / "case.jsonl").read_text(encoding="utf-8").splitlines()
    assert (
        len(lines) == 1
        and json.loads(lines[0])["request"]["messages"][0]["content"] == "incident"
    )
    assert convo.spent == pytest.approx(2.0 + 5 * 10 / 1e6)


def test_a_refusal_fails_the_case() -> None:
    fake = Fake(
        [
            reply(
                [],
                "refusal",
                stop_details={
                    "type": "refusal",
                    "category": "cyber",
                    "explanation": None,
                },
            )
        ]
    )
    with pytest.raises(ModelFailed, match="declined"):
        conversation(fake).ask()
