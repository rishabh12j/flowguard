"""Converting RCAEval RE3 cases, and scoring a run by the root-cause service."""

import csv
import json
from datetime import UTC, datetime, timedelta

import pytest

from flowguard.benchmark import rcaeval
from flowguard.benchmark.rcaeval import (
    Pattern,
    convert,
    infer_level,
    log_line,
    select,
    template,
    traced_calls,
    within_budget,
)
from flowguard.dataset import load_evidence, load_ground_truth, load_profile
from flowguard.domain.signals import kind_of
from flowguard.evaluation.rcaeval import score

START = datetime(2024, 11, 22, 3, 6, tzinfo=UTC)


@pytest.mark.parametrize(
    ("message", "level"),
    [
        (
            "2024-11-22 03:06:13.622 ERROR [orders,,,] 6 --- Servlet.service() threw",
            "ERROR",
        ),
        ("2024-11-22 02:40:21.098  INFO [carts] Exception in monitor thread", "INFO"),
        (
            '{"t":{"$date":"2024"},"s":"I",  "c":"NETWORK", "msg":"Connection ended"}',
            "INFO",
        ),
        ('{"level":"warning","msg":"slow call"}', "WARN"),
        ("failed to send order confirmation: rpc error: code = Unavailable", "ERROR"),
        ("POST /cart 500 44.006 ms - 64", "ERROR"),
        ("GET /catalogue 200 3.1 ms - 12", "INFO"),
        ("request started", "INFO"),
    ],
)
def test_the_level_is_read_from_the_message(message, level):
    assert infer_level(message) == level


def test_messages_that_differ_only_in_values_share_a_pattern():
    first = "2024-11-22 03:06:13 GetCart called with userId=418ce0b6-15a4-4228-a6cf-27e322509121"
    second = "2024-11-22 03:07:55 GetCart called with userId=9a40d526-45ff-488a-a623-84469e356f95"

    assert template(first) == template(second) == "GetCart called with userId=<uuid>"
    assert template("set cookie5ff2c3b1df0c6b") == template("set cookie9aa1d7b2df4c6e")


def pattern(service, level, before=0, after=0, text="x"):
    found = Pattern(service, f"{service} {text}", level, before, after)
    if before:
        found.first_before = START - timedelta(minutes=2)
        found.example_before = f"{service} {text} early"
    if after:
        found.first_after = START + timedelta(minutes=1)
        found.example_after = f"{service} {text} late"
    return found


def test_errors_after_the_start_come_first_new_ones_before_old_ones():
    found = {
        ("a", "old"): pattern("a", "ERROR", before=50, after=60, text="old"),
        ("b", "new"): pattern("b", "WARN", after=5, text="new"),
        ("c", "info"): pattern("c", "INFO", after=9, text="info"),
        ("d", "steady"): pattern("d", "INFO", before=9, after=9, text="steady"),
        ("e", "stopped"): pattern("e", "ERROR", before=4, text="stopped"),
    }

    chosen = select(found)

    assert [p.template for p in chosen] == [
        "b new",
        "a old",
        "c info",
        "e stopped",
    ]


def errors(services):
    return {
        (s, str(n)): pattern(s, "ERROR", after=10 + n, text=str(n))
        for s in services
        for n in range(6)
    }


def test_each_service_is_capped_and_the_total_too():
    few = select(errors("abc"))
    many = select(errors("abcdefghijklmnop"))

    assert [sum(p.service == s for p in few) for s in "abc"] == [4, 4, 4]
    assert len(many) == rcaeval.MAX_LINES


def test_a_pattern_seen_before_the_start_is_shown_when_first_seen():
    old = log_line(pattern("a", "ERROR", before=3, after=7))
    new = log_line(pattern("b", "ERROR", after=7))

    assert old["timestamp"] < START <= new["timestamp"]
    # The connector only counts; FlowGuard words what the counts mean.
    assert old["message"] == "a x early"
    assert new["metadata"] == {
        "count_before": 0,
        "count_after": 7,
        "minutes_before": 5.0,
        "minutes_after": 10.0,
    }


def test_lines_are_kept_in_order_of_importance_within_the_budget():
    lines = [{"message": "m" * 4000} for _ in range(5)]

    assert len(within_budget(lines)) == 3


def write_csv(path, fields, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def test_calls_traced_before_the_injection_become_edges(tmp_path):
    cutoff = START.timestamp() * 1000
    fields = [
        "spanID",
        "serviceName",
        "operationName",
        "startTimeMillis",
        "parentSpanID",
    ]
    write_csv(
        tmp_path / "traces.csv",
        fields,
        [
            {
                "spanID": "1",
                "serviceName": "frontend",
                "operationName": "GET",
                "startTimeMillis": cutoff - 10,
                "parentSpanID": "",
            },
            {
                "spanID": "2",
                "serviceName": "cart",
                "operationName": "Get",
                "startTimeMillis": cutoff - 9,
                "parentSpanID": "1",
            },
            {
                "spanID": "3",
                "serviceName": "email",
                "operationName": "Send",
                "startTimeMillis": cutoff + 5,
                "parentSpanID": "1",
            },
            {
                "spanID": "4",
                "serviceName": "otel",
                "operationName": "opentelemetry.Export",
                "startTimeMillis": cutoff - 8,
                "parentSpanID": "1",
            },
        ],
    )

    # The cart's answers flow to the frontend; the email call came after the fault.
    assert traced_calls(tmp_path, START) == {("cart", "frontend")}


def raw_case(raw, folder, run, injected, rows):
    case = raw / "RE3-SS" / folder / str(run)
    case.mkdir(parents=True)
    (case / "inject_time.txt").write_text(str(int(injected.timestamp())))
    write_csv(
        case / "logs.csv",
        ["time", "timestamp", "container_name", "message"],
        [
            {
                "time": "",
                "timestamp": int((injected + offset).timestamp() * 1e9),
                "container_name": service,
                "message": message,
            }
            for offset, service, message in rows
        ],
    )


ROWS = [
    (timedelta(minutes=-3), "queue-master", "ERROR could not launch worker"),
    (timedelta(minutes=2), "queue-master", "ERROR could not launch worker"),
    (timedelta(minutes=1), "carts", "WARN Request method 'POST' not supported"),
    (timedelta(minutes=1, seconds=5), "orders", "ERROR 503 Service Unavailable"),
    (timedelta(minutes=20), "orders", "ERROR outside the window"),
]


def converted(tmp_path):
    raw = tmp_path / "raw"
    raw_case(raw, "carts_f3", 1, START, ROWS)
    raw_case(raw, "orders_f1", 1, START + timedelta(hours=1), ROWS[2:4])
    # A stray file beside the case folders, as in the download, is not a case.
    (raw / "RE3-SS" / ".DS_Store").write_text("")
    out = tmp_path / "out"
    assert convert(raw, "SS", "dev", out) == 2
    return out


def test_cases_become_incidents_with_their_own_window_and_label(tmp_path):
    out = converted(tmp_path)

    truth = load_ground_truth("RE3-SS-001", out)
    incident = json.loads((out / "incidents" / "RE3-SS-001.json").read_text())
    logs = [item for item in load_evidence(out) if item.source_type == "log"]
    assert truth.root_cause_service == "carts"
    assert truth.family == "carts_f3"
    assert truth.category == "deployment_or_configuration"
    assert incident["description"].endswith("since about 03:06 UTC.")
    assert incident["affected_system"] == "sock-shop"
    first = [i for i in logs if i.timestamp < START + timedelta(minutes=30)]
    assert len(first) == 3
    assert not any("outside the window" in i.content for i in logs)
    assert [i.evidence_id for i in logs] == [f"LOG-{n:05d}" for n in range(1, 6)]
    # The faulty service's line after the start is what proves the cause.
    carts = next(i for i in first if i.source_name == "carts")
    assert truth.required_evidence_ids == [carts.evidence_id]
    assert any(i.source_type == "dependency_map" for i in load_evidence(out))
    # The testbed keeps no record of the release that carried the fault.
    assert load_profile(out).recorded_changes == ()
    queue = next(i for i in first if i.source_name == "queue-master")
    assert (kind_of(queue), kind_of(carts)) == ("steady", "new")


def test_cases_that_overlap_in_time_are_refused(tmp_path):
    raw = tmp_path / "raw"
    raw_case(raw, "carts_f3", 1, START, ROWS[:1])
    raw_case(raw, "carts_f3", 2, START + timedelta(minutes=10), ROWS[:1])

    with pytest.raises(ValueError, match="overlap"):
        convert(raw, "SS", "dev", tmp_path / "out")


def journal(path, results):
    with open(path / "evaluation-dev.journal.jsonl", "w", encoding="utf-8") as f:
        for incident_id, category, service, *located in results:
            result = {
                "incident_id": incident_id,
                "family": "carts_f3" if incident_id.endswith("1") else "orders_f1",
                "expected_outcome": "diagnose",
                "status": "diagnosed",
                "seconds": 1.0,
                "expected_category": "deployment_or_configuration",
                "category": category,
                "correct": False,
                "top_3_hit": False,
                "confidence": None,
                "evidence_precision": 0.0,
                "required_evidence_recall": 0.0,
                "tool_calls": 1,
                "tool_calls_ok": 1,
                "claims": 0,
                "unsupported_claims": 0,
                "planned": [],
                "plan_recall": None,
                "plan_precision": None,
                "change_precision": None,
                "fix_expected": False,
                "fix_planned": False,
                "rejected_steps": 0,
                "rejected": [],
                "hypothesis_categories": [],
                "unsafe_steps": [],
                "approval_bypassed": False,
                "root_cause_service": service,
                "located": bool(located),
                "abstention": "isolated" if category == "unknown" else None,
            }
            f.write(json.dumps({"result": result, "abstention": {}}) + "\n")


def test_a_run_is_scored_by_the_service_with_two_baselines(tmp_path):
    out = converted(tmp_path)
    report = tmp_path / "report"
    report.mkdir()
    journal(
        report,
        [("RE3-SS-001", "networking", "carts"), ("RE3-SS-002", "unknown", "orders")],
    )

    result = score(out, report, "dev")

    assert (result.counts.right, result.counts.wrong, result.counts.abstained) == (
        1,
        0,
        1,
    )
    assert result.precision == 1.0
    assert result.right_service_when_abstained == 1
    assert result.by_fault["f3"].right == 1
    # One case each for carts and orders, so always guessing one is right once.
    assert result.majority_baseline == 0.5
    # In both cases the first new error after the start is in orders.
    assert result.first_error_baseline == 0.5
    # carts and orders both have new problems, and orders depends on carts, so
    # the deepest service is carts in both cases: right once.
    assert result.deepest_baseline == 0.5
    assert not result.partial


def test_a_located_service_counts_as_named_and_is_reported_apart(tmp_path):
    out = converted(tmp_path)
    report = tmp_path / "report"
    report.mkdir()
    journal(
        report,
        [
            ("RE3-SS-001", "unknown", "carts", True),
            ("RE3-SS-002", "unknown", "carts", True),
        ],
    )

    result = score(out, report, "dev")

    counts = result.counts
    assert (counts.right, counts.located, counts.wrong, counts.abstained) == (
        0,
        1,
        1,
        0,
    )
    assert result.accuracy == 0.5 and result.precision == 0.5
    assert result.by_service["carts"].located == 1
