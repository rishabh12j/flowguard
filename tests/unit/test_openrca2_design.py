"""The design's first parts: the lead agent's prompting and the code survey."""

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

pa = pytest.importorskip("pyarrow")
pq = pytest.importorskip("pyarrow.parquet")
pytest.importorskip("duckdb")
anthropic = pytest.importorskip("anthropic")
httpx2 = pytest.importorskip("httpx2")

from flowguard.llm.claude import claude_schema  # noqa: E402
from flowguard.openrca2 import TELEMETRY_FILES  # noqa: E402
from flowguard.openrca2.access import CaseTelemetry  # noqa: E402
from flowguard.openrca2.baseline import ANSWER_SCHEMA, INCIDENT, agents  # noqa: E402
from flowguard.openrca2.chat import ToolSpec  # noqa: E402
from flowguard.openrca2.chat_claude import ClaudeConversation  # noqa: E402
from flowguard.openrca2.survey import entries, pod_service, survey  # noqa: E402

T0 = datetime(2026, 5, 1, tzinfo=UTC)


def table(rows: list[dict[str, Any]], columns: dict[str, Any]) -> Any:
    return pa.table(
        {
            name: pa.array([r.get(name) for r in rows], type)
            for name, type in columns.items()
        }
    )


TRACE = {
    "time": pa.timestamp("us", tz="UTC"), "trace_id": pa.string(), "span_id": pa.string(),
    "parent_span_id": pa.string(), "service_name": pa.string(), "span_name": pa.string(),
    "duration": pa.uint64(), "attr.status_code": pa.string(), "attr.http.response.status_code": pa.uint16(),
    "attr.k8s.pod.name": pa.string(),
}  # fmt: skip
LOG = {
    "time": pa.timestamp("us", tz="UTC"),
    "service_name": pa.string(),
    "level": pa.string(),
    "message": pa.string(),
}
METRIC = {
    "time": pa.timestamp("us", tz="UTC"), "service_name": pa.string(), "metric": pa.string(), "value": pa.float64(),
    "attr.k8s.pod.name": pa.string(), "attr.source": pa.string(), "attr.destination": pa.string(),
}  # fmt: skip


def spans(start: datetime, broken: bool) -> list[dict[str, Any]]:
    """Load generator -> a -> b, one trace a second for five minutes."""
    rows = []
    for i in range(300):
        t = start + timedelta(seconds=i)
        trace = f"{start.minute}-{i}"
        rows += [
            {"time": t, "trace_id": trace, "span_id": f"{trace}-lg", "parent_span_id": "", "service_name": "loadgenerator",
             "duration": 9_000_000, "attr.status_code": "Unset", "attr.k8s.pod.name": "loadgenerator-1"},
            {"time": t, "trace_id": trace, "span_id": f"{trace}-a", "parent_span_id": f"{trace}-lg", "service_name": "a",
             "duration": 8_000_000, "attr.status_code": "Unset", "attr.k8s.pod.name": "a-5f6d7c8b9-abcde"},
            {"time": t, "trace_id": trace, "span_id": f"{trace}-b", "parent_span_id": f"{trace}-a", "service_name": "b",
             "duration": 5_000_000, "attr.status_code": "Error" if broken else "Unset",
             "attr.http.response.status_code": 500 if broken else 200,
             "attr.k8s.pod.name": "b-7c9d8e6f5-zzzzz" if broken else "b-7c9d8e6f5-yyyyy"},
        ]  # fmt: skip
    return rows


def metrics(start: datetime, broken: bool, hubble: bool) -> list[dict[str, Any]]:
    rows = []
    for i in range(10):
        t = start + timedelta(seconds=30 * i)
        rows.append(
            {
                "time": t,
                "service_name": "b",
                "metric": "k8s.container.restarts",
                "value": 3.0 if broken else 0.0,
            }
        )
        rows.append(
            {
                "time": t,
                "service_name": "a",
                "metric": "jvm.memory.used",
                "value": 100.0 + i % 2,
            }
        )
        # Two metrics of `a` that shift by exactly the same amount, the later
        # name first, so a tie broken by row order would pick the wrong one.
        for name in ("a.tied.second", "a.tied.first"):
            rows.append(
                {
                    "time": t,
                    "service_name": "a",
                    "metric": name,
                    "value": (200.0 if broken else 100.0) + i % 2,
                }
            )
        if hubble:
            rows.append({"time": t, "service_name": "a", "metric": "hubble_flows_processed_total",
                         "value": 200.0 if broken else 100.0, "attr.source": "ns/a-5f6d7c8b9-abcde",
                         "attr.destination": "ns/b-7c9d8e6f5-yyyyy"})  # fmt: skip
    return rows


def make_case(root: Path, case_id: str, hubble: bool) -> CaseTelemetry:
    folder = root / "dev" / case_id
    folder.mkdir(parents=True)
    starts = {"normal": T0, "abnormal": T0 + timedelta(minutes=5)}
    for name in TELEMETRY_FILES:
        period, kind = name.removesuffix(".parquet").split("_", 1)
        broken = period == "abnormal"
        if kind == "traces":
            data = table(spans(starts[period], broken), TRACE)
        elif kind == "logs":
            data = table(
                [
                    {
                        "time": starts[period],
                        "service_name": "b",
                        "level": "ERROR" if broken else "INFO",
                        "message": "x",
                    }
                ],
                LOG,
            )
        elif kind == "metrics_sum":
            data = table(metrics(starts[period], broken, hubble), METRIC)
        else:
            data = table(
                metrics(starts[period], broken, False) if kind == "metrics" else [],
                METRIC,
            )
        pq.write_table(data, folder / name)
    return CaseTelemetry(root / "dev", case_id)


def test_the_survey_shows_what_changed(tmp_path: Path) -> None:
    case = make_case(tmp_path, "case-001", hubble=True)
    text = survey(case.connect())
    services = text.split("### Services")[1].split("### Entry")[0]
    rows = {
        line.split("|")[1].strip(): line
        for line in services.splitlines()
        if line.startswith("| ") and "→" in line
    }
    assert "0.00 → 1.00" in rows["b"]  # every span of b fails
    assert "| 3 |" in rows["b"] and "| 1 |" in rows["b"]  # three restarts, one new pod
    assert "0.00 → 0.00" in rows["a"]
    assert "| a.tied.first (" in rows["a"]  # a tie goes to the first name
    assert "loadgenerator" not in rows
    assert "Entry services (requests arrive here): a" in text
    calls = text.split("### Calls")[1].split("### Network")[0]
    assert (
        "| a | b | 60.2 → 60.2 | 0.00 → 1.00 |" in calls
    )  # 300 calls in a 299-second window
    assert "| a | b | 100.0 → 200.0 | 0.0 → 0.0 |" in text


def test_the_survey_says_when_network_metrics_are_missing(tmp_path: Path) -> None:
    case = make_case(tmp_path, "case-002", hubble=False)
    assert "Per-connection network metrics are not recorded in this case." in survey(
        case.connect()
    )
    assert entries(case.connect()) == ["a"]


@pytest.mark.parametrize(
    ("pod", "service"),
    [
        ("ts2/ts-price-service-6b784db86c-68ks4", "ts-price-service"),
        ("ts2/mysql-0", "mysql"),
        ("", ""),
        (None, ""),
    ],
)
def test_pods_are_mapped_to_services(pod: str | None, service: str) -> None:
    assert pod_service(pod) == service


def test_the_lead_prompt_says_how_answers_are_judged() -> None:
    lead = agents()["lead"]
    for words in (
        "at the calling service",
        "at either end",
        "effect reached beyond its own service",
        "fault_kind enum",
    ):
        assert words in lead.system
    assert lead.answer_system is None and lead.answer_schema is ANSWER_SCHEMA
    assert agents()["standard"].answer_schema is None


def test_the_survey_follows_the_incident_text(tmp_path: Path) -> None:
    case = make_case(tmp_path, "case-003", hubble=False)
    first = agents()["lead+survey"].first(case)
    assert (
        first.startswith(INCIDENT)
        and "## Survey of this case, computed by code" in first
    )
    assert agents()["lead"].first(case) == INCIDENT


def test_the_answer_schema_is_strict() -> None:
    objects = [ANSWER_SCHEMA, ANSWER_SCHEMA["properties"]["root_causes"]["items"],
               ANSWER_SCHEMA["properties"]["propagation"]["items"],
               ANSWER_SCHEMA["properties"]["root_causes"]["items"]["properties"]["evidence"]["items"]]  # fmt: skip
    assert all(o["additionalProperties"] is False for o in objects)


def test_an_answer_names_at_least_one_fault() -> None:
    # Five of the lead's first 100 answers were empty; every case has a fault.
    assert ANSWER_SCHEMA["properties"]["root_causes"]["minItems"] == 1
    sent = claude_schema(ANSWER_SCHEMA)
    assert sent["properties"]["root_causes"]["minItems"] == 1


class Fake:
    def __init__(self, replies: list[dict[str, Any]]) -> None:
        self.replies, self.bodies = replies, []

    def __call__(self, request: Any) -> Any:
        self.bodies.append(json.loads(request.content))
        return httpx2.Response(200, json=self.replies.pop(0))


def reply(content: list[dict[str, Any]], stop: str) -> dict[str, Any]:
    usage = {
        "input_tokens": 1,
        "output_tokens": 1,
        "cache_creation_input_tokens": 0,
        "cache_read_input_tokens": 0,
    }
    return {"id": "m", "type": "message", "role": "assistant", "model": "claude-haiku-5-5", "content": content,
            "stop_reason": stop, "stop_sequence": None, "usage": usage}  # fmt: skip


def test_the_lead_answer_turn_keeps_its_history_and_sends_the_schema() -> None:
    turn = [{"type": "thinking", "thinking": "", "signature": "s"},
            {"type": "tool_use", "id": "t", "name": "think_tool", "input": {"reflection": "x"}}]  # fmt: skip
    fake = Fake(
        [
            reply(turn, "tool_use"),
            reply([{"type": "text", "text": "{}", "citations": None}], "end_turn"),
        ]
    )
    client = anthropic.Anthropic(
        api_key="x",
        max_retries=0,
        http_client=anthropic.DefaultHttpxClient(transport=httpx2.MockTransport(fake)),
    )
    tool = ToolSpec(
        "think_tool",
        "note",
        {"type": "object", "properties": {"reflection": {"type": "string"}}},
    )
    convo = ClaudeConversation(
        "claude-haiku-5-5", "investigate", "incident", [tool], client=client
    )
    first = convo.ask()
    convo.answer_tools([(first.calls[0], "ok")])
    convo.conclude(None, "answer now", ANSWER_SCHEMA)
    body = fake.bodies[1]
    assert body["system"] == "investigate" and body["tool_choice"] == {"type": "none"}
    assert (
        body["messages"][1]["content"] == turn
    )  # the thinking block is replayed untouched
    assert body["output_config"]["format"]["type"] == "json_schema"
    assert "enum" in json.dumps(body["output_config"]["format"]["schema"])
