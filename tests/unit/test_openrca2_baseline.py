"""The rebuilt standard agent, with a scripted model: no model is called."""

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from flowguard.openrca2 import TELEMETRY_FILES
from flowguard.openrca2.access import CaseTelemetry
from flowguard.openrca2.chat import ToolCall, Turn, Usage

pa = pytest.importorskip("pyarrow")
pq = pytest.importorskip("pyarrow.parquet")
pytest.importorskip("duckdb")

from flowguard.openrca2.baseline import (  # noqa: E402
    BUDGET_SPENT,
    Tools,
    investigate,
    sample,
)
from flowguard.openrca2.chat_claude import cost  # noqa: E402

T0 = datetime(2026, 5, 1, tzinfo=UTC)
ANSWER = {
    "root_causes": [
        {
            "service": "a",
            "fault_kind": "pod_failure",
            "evidence": [{"kind": "trace", "sql": "SELECT 1", "claim": "x"}],
        }
    ],
    "propagation": [],
}


@pytest.fixture
def case(tmp_path: Path) -> CaseTelemetry:
    folder = tmp_path / "dev" / "case-001"
    folder.mkdir(parents=True)
    for name in TELEMETRY_FILES:
        n = 40
        data = {
            "time": [T0 + timedelta(seconds=i) for i in range(n)],
            "service_name": ["a" if i % 2 else "b" for i in range(n)],
            "attr.status_code": ["Error" if i % 4 == 1 else "Unset" for i in range(n)],
            "message": ["x" * 2000] * n,
        }
        pq.write_table(pa.table(data), folder / name)
    answers = tmp_path / "answers" / "dev" / "case-001"
    answers.mkdir(parents=True)
    (answers / "label.json").write_text('{"secret": true}', encoding="utf-8")
    return CaseTelemetry(tmp_path / "dev", "case-001")


def call(name: str, **arguments: Any) -> ToolCall:
    return ToolCall(f"id-{name}", name, arguments)


class Scripted:
    """A conversation that plays back fixed turns, then a fixed answer."""

    def __init__(self, turns: list[list[ToolCall]], answer: str) -> None:
        self.turns = turns
        self.answer = answer
        self.results: list[list[tuple[ToolCall, str]]] = []
        self.concluded: tuple[str, str] | None = None

    def ask(self) -> Turn:
        calls = self.turns.pop(0) if self.turns else []
        return Turn(
            "",
            calls,
            Usage(prompt=100, output=10, usd=0.01),
            "tool_use" if calls else "end_turn",
        )

    def answer_tools(self, results: list[tuple[ToolCall, str]]) -> None:
        self.results.append(results)

    def conclude(self, system: str | None, prompt: str, schema: Any = None) -> Turn:
        self.concluded = (system, prompt)
        return Turn(self.answer, [], Usage(prompt=200, output=50, usd=0.02), "end_turn")

    def transcript(self) -> list[dict[str, Any]]:
        return []


def test_the_loop_runs_tools_then_asks_for_the_answer(case: CaseTelemetry) -> None:
    turns = [
        [call("list_tables_in_directory", directory=".")],
        [call("think_tool", reflection="plan")],
    ]
    convo = Scripted(turns, json.dumps(ANSWER))
    run = investigate(convo, Tools(case))
    assert run.calls == {"list_tables_in_directory": 1, "think_tool": 1}
    assert run.turns == 4  # two with calls, one without, and the answer
    assert run.stopped == "the model stopped calling tools"
    assert run.answer is not None and run.answer.root_causes[0].service == "a"
    assert run.usage.prompt == 500 and run.usage.usd == pytest.approx(0.05)
    assert run.per_turn == [(100, 10), (100, 10), (100, 10), (200, 50)]
    assert convo.concluded is not None and "fault_kind enum" in convo.concluded[0]


def test_a_fenced_answer_is_read_and_a_broken_one_is_none(case: CaseTelemetry) -> None:
    assert (
        investigate(
            Scripted([], "```json\n" + json.dumps(ANSWER) + "\n```"), Tools(case)
        ).answer
        is not None
    )
    assert investigate(Scripted([], "The root cause is a."), Tools(case)).answer is None


def test_the_cap_stops_the_loop_and_refuses_extra_calls(case: CaseTelemetry) -> None:
    turns = [
        [call("think_tool", reflection=str(i)) for i in range(3)] for _ in range(5)
    ]
    convo = Scripted(turns, json.dumps(ANSWER))
    run = investigate(convo, Tools(case), max_calls=4)
    assert sum(run.calls.values()) == 4
    assert run.stopped == "the cap of 4 tool calls"
    assert [r for _, r in convo.results[1]] == [
        "Reflection recorded: 0",
        BUDGET_SPENT,
        BUDGET_SPENT,
    ]


def test_the_spending_limit_stops_the_loop(case: CaseTelemetry) -> None:
    turns = [[call("think_tool", reflection="x")]] * 10
    run = investigate(
        Scripted(turns, json.dumps(ANSWER)), Tools(case), budget=lambda usd: usd < 0.025
    )
    assert run.stopped == "the spending limit" and run.turns == 4


def test_the_tools_show_underscored_columns_and_ten_rows(case: CaseTelemetry) -> None:
    tools = Tools(case)
    tables = json.loads(tools.run(call("list_tables_in_directory", directory=".")))
    assert {t["table"] for t in tables} == {
        n.removesuffix(".parquet") for n in TELEMETRY_FILES
    }
    schema = json.loads(
        tools.run(call("get_schema", parquet_files=["abnormal_traces"]))
    )
    assert "attr_status_code" in [c["name"] for c in schema["columns"]]
    rows = json.loads(
        tools.run(
            call(
                "query_parquet_files",
                parquet_files="abnormal_traces",
                query="SELECT service_name FROM abnormal_traces",
            )
        )
    )
    assert len(rows) == 10
    by_file = tools.run(
        call(
            "query_parquet_files",
            parquet_files=[],
            query="SELECT count(*) AS n FROM read_parquet('abnormal_logs.parquet')",
        )
    )
    assert json.loads(by_file) == [{"n": 40}]


def test_a_big_result_is_refused_with_advice(case: CaseTelemetry) -> None:
    result = json.loads(
        Tools(case).run(
            call(
                "query_parquet_files",
                parquet_files=["abnormal_logs"],
                query="SELECT message FROM abnormal_logs",
                limit=40,
            )
        )
    )
    assert result["error"] == "Result exceeds token budget"


def test_a_query_cannot_reach_an_answer_file_and_does_not_show_paths(
    case: CaseTelemetry,
) -> None:
    tools = Tools(case)
    answers = (
        case.path("normal_logs.parquet").parents[3]
        / "answers"
        / "dev"
        / "case-001"
        / "label.json"
    )
    result = json.loads(
        tools.run(
            call(
                "query_parquet_files",
                parquet_files=[],
                query=f"SELECT * FROM read_json_auto('{answers.as_posix()}')",
            )
        )
    )
    assert "error" in result and "secret" not in json.dumps(result)
    assert str(case.path("normal_logs.parquet").parent) not in tools.run(
        call("query_parquet_files", parquet_files=[], query="SELECT * FROM nowhere")
    )


def test_evidence_queries_are_graded_like_the_judge(case: CaseTelemetry) -> None:
    tools = Tools(case)
    assert tools.sql_status("SELECT 1") == "OK"
    assert (
        tools.sql_status("SELECT * FROM abnormal_traces WHERE service_name = 'zzz'")
        == "EMPTY"
    )
    assert tools.sql_status("SELEC nonsense") == "SQL_ERROR"


def test_the_sample_is_fixed_and_proportional() -> None:
    split = [
        {"id": f"case-{i:03d}", "system": s, "split": "dev"}
        for i, s in enumerate(["ts"] * 60 + ["hs"] * 33 + ["otel-demo"] * 7)
    ]
    split.append({"id": "case-999", "system": "ts", "split": "held-out"})
    chosen = sample(split, 10)
    systems = {c["id"]: c["system"] for c in split}
    assert sorted(systems[c] for c in chosen).count("ts") == 6
    assert sorted(systems[c] for c in chosen).count("hs") == 3
    assert "case-999" not in chosen and chosen == sample(split, 10)


def test_claude_cost_uses_cache_prices_and_haikus_long_prompt_price() -> None:
    small = Usage(prompt=10_000, cache_write=2_000, cache_read=6_000, output=1_000)
    assert cost("claude-haiku-5-5", small) == pytest.approx(
        (2_000 * 0.10 + 2_000 * 0.125 + 6_000 * 0.01 + 1_000 * 0.50) / 1e6
    )
    big = Usage(prompt=200_000, output=1_000)
    assert cost("claude-haiku-5-5", big) == pytest.approx(
        (200_000 * 0.50 + 1_000 * 2.50) / 1e6
    )
    assert cost("unknown-model", big) == 0.0


def test_an_answer_turn_that_calls_a_tool_is_noted(case: CaseTelemetry) -> None:
    class CallsInstead(Scripted):
        def conclude(self, system: str | None, prompt: str, schema: Any = None) -> Turn:
            return Turn("", [call("think_tool", reflection="more")], Usage(), "stop")

    run = investigate(CallsInstead([], ""), Tools(case))
    assert (
        run.answer is None
        and "the answer turn called a tool instead of answering" in run.notes
    )


def test_the_json_answer_schema_holds_only_the_official_kinds() -> None:
    from flowguard.openrca2.baseline import ANSWER_SCHEMA
    from flowguard.openrca2.score import KINDS

    item = ANSWER_SCHEMA["properties"]["root_causes"]["items"]
    assert (
        set(item["properties"]["fault_kind"]["enum"]) == set(KINDS) and len(KINDS) == 25
    )
    assert item["properties"]["evidence"]["minItems"] == 1


def test_a_local_answer_turn_sends_the_schema_and_no_tools() -> None:
    import httpx

    from flowguard.openrca2.chat_ollama import OllamaConversation

    sent: list[dict[str, Any]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        sent.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "message": {"role": "assistant", "content": "{}"},
                "done_reason": "stop",
            },
        )

    schema = {"type": "object"}
    convo = OllamaConversation(
        "m",
        "sys",
        "go",
        [],
        answer_format=schema,
        transport=httpx.MockTransport(handler),
    )
    convo.ask()
    convo.conclude("synth", "answer")
    assert (
        "format" not in sent[0]
        and sent[1]["format"] == schema
        and "tools" not in sent[1]
    )
    assert sent[1]["messages"][0] == {"role": "system", "content": "synth"}


def test_a_local_500_is_retried_and_its_message_kept() -> None:
    import httpx

    from flowguard.openrca2.chat import ModelFailed
    from flowguard.openrca2.chat_ollama import OllamaConversation

    replies = [
        httpx.Response(
            500, json={"error": "error parsing tool call: invalid character"}
        ),
        httpx.Response(
            200,
            json={
                "message": {"role": "assistant", "content": "ok"},
                "done_reason": "stop",
            },
        ),
    ]
    convo = OllamaConversation(
        "m", "s", "go", [], transport=httpx.MockTransport(lambda r: replies.pop(0))
    )
    turn = convo.ask()
    assert turn.text == "ok" and turn.notes == [
        "Ollama failed and the request was retried: error parsing tool call: invalid character"
    ]

    always = OllamaConversation(
        "m",
        "s",
        "go",
        [],
        transport=httpx.MockTransport(
            lambda r: httpx.Response(500, json={"error": "bad"})
        ),
    )
    with pytest.raises(ModelFailed, match="after 5 retries"):
        always.ask()
