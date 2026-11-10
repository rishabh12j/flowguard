import asyncio
import json
from datetime import UTC, datetime

from flowguard.domain.evidence import EvidenceItem
from flowguard.domain.incidents import Incident
from flowguard.evaluation.what_failed import (
    ProbeResult,
    Score,
    answer_schema,
    ask,
    decide,
    gather,
    judge,
    neutral_ids,
    score,
)
from flowguard.graph.context import EvidenceUnavailable, Found
from flowguard.llm.client import ModelDeclined

INCIDENT = Incident(
    incident_id="BENCH-0001",
    description="Lookups in orders-processor are timing out.",
    affected_system="orders",
    start_time=datetime(2027, 2, 9, 13, tzinfo=UTC),
    end_time=datetime(2027, 2, 9, 15, tzinfo=UTC),
)


def item(evidence_id, source_type, content="", level=None, minute=0):
    return EvidenceItem(
        evidence_id=evidence_id,
        source_type=source_type,
        source_name="orders-processor",
        timestamp=datetime(2027, 2, 9, 13, minute, tzinfo=UTC) if level else None,
        # Real titles are an exception type or a document's title, never its ID.
        title=f"{source_type} title",
        content=content,
        metadata={"level": level} if level else {},
    )


ERROR = item("LOG-00089", "log", "Query on orders-db timed out after 10 s", "ERROR", 11)
INFO = item("LOG-00088", "log", "Processed a batch normally", "INFO", 2)
SPEC = item("SPEC-ORDERS-T2#timeouts", "api_spec", "Queries are cancelled after 10 s.")
RUNBOOK = item("RB-ORDERS-T2", "runbook", "Restore the index.")
PAST = item("HIST-ORDERS-T2", "historical_incident", "An index was dropped.")
MAP = item("DEPMAP-ORDERS", "dependency_map", "orders-processor -> orders-db")


class FakeTools:
    """Serves fixed evidence and records which tools were asked."""

    def __init__(self, fail_documents=False):
        self.asked = []
        self.fail_documents = fail_documents

    async def search_logs(self, start_time, end_time):
        self.asked.append("search_logs")
        return Found([INFO, ERROR])

    async def search_runbooks(self, query, system):
        self.asked.append("search_runbooks")
        if self.fail_documents:
            raise EvidenceUnavailable("the knowledge server timed out")
        return Found([RUNBOOK, SPEC, PAST])

    async def get_dependency_map(self, service):
        self.asked.append(f"get_dependency_map {service}")
        return Found([MAP])

    async def get_deployments(self, start_time, end_time):
        self.asked.append("get_deployments")
        return Found([])

    async def search_alerts(self, start_time, end_time):
        self.asked.append("search_alerts")
        return Found([])

    async def get_metrics(self, service, start_time, end_time):
        self.asked.append("get_metrics")
        return Found([])


class FakeLLM:
    def __init__(self, answer=None, error=None):
        self.answer = answer
        self.error = error
        self.calls = []

    def generate(self, system, prompt, schema):
        self.calls.append((system, prompt, schema))
        if self.error is not None:
            raise self.error
        return json.dumps(self.answer)


def answer(category, *ids, failure="Queries on orders-db time out."):
    return {"failure": failure, "evidence_ids": list(ids), "category": category}


def test_only_symptoms_are_gathered():
    tools = FakeTools()

    evidence, problems = asyncio.run(gather(tools, INCIDENT))

    # No changes are asked for, and precedents are dropped from the search.
    assert tools.asked == [
        "search_logs",
        "search_runbooks",
        "get_dependency_map orders-processor",
    ]
    assert evidence == [INFO, ERROR, SPEC, MAP]
    assert problems == []


def test_a_failed_tool_loses_only_its_own_evidence():
    evidence, problems = asyncio.run(gather(FakeTools(fail_documents=True), INCIDENT))

    assert evidence == [INFO, ERROR, MAP]
    assert problems == ["the knowledge server timed out"]


def test_the_model_sees_neutral_ids_only():
    llm = FakeLLM(answer("timeout", "E2"))

    ask(INCIDENT, [INFO, ERROR, SPEC, MAP], llm)

    system, prompt, schema = llm.calls[0]
    assert "ID: E1" in prompt and "ID: E4" in prompt
    for original in ("LOG-00089", "SPEC-ORDERS-T2", "DEPMAP-ORDERS", "BENCH-0001"):
        assert original not in prompt
    assert "Type: log (ERROR)" in prompt
    assert "what failed, not what changed" in system
    assert schema["properties"]["evidence_ids"]["items"]["enum"] == [
        "E1",
        "E2",
        "E3",
        "E4",
    ]


def test_the_schema_asks_for_the_failure_before_the_category():
    assert list(answer_schema(["E1"])["properties"]) == [
        "failure",
        "evidence_ids",
        "category",
    ]


def test_a_category_citing_a_log_is_accepted_with_the_original_ids():
    decision = decide(
        json.dumps(answer("timeout", "E2", "E3")), neutral_ids([INFO, ERROR, SPEC])
    )

    assert decision.category == "timeout"
    assert decision.cited == ["LOG-00089", "SPEC-ORDERS-T2#timeouts"]
    assert decision.reason is None


def test_a_category_citing_no_log_is_not_accepted():
    decision = decide(
        json.dumps(answer("timeout", "E3")), neutral_ids([INFO, ERROR, SPEC])
    )

    assert decision.answered == "timeout"
    assert decision.category == "unknown"
    assert decision.reason == "the answer cites no log"


def test_unknown_is_the_models_answer():
    decision = decide(json.dumps(answer("unknown")), neutral_ids([INFO]))

    assert (decision.answered, decision.category) == ("unknown", "unknown")


def test_a_broken_answer_or_invented_id_is_unknown_not_a_crash():
    shown = neutral_ids([INFO, ERROR])

    broken = decide("not json", shown)
    invented = decide(json.dumps(answer("timeout", "E9")), shown)

    assert broken.category == "unknown" and broken.answered is None
    assert invented.category == "unknown"
    assert "E9" in (invented.reason or "")


def test_a_refusal_or_no_evidence_is_unknown():
    declined = ask(INCIDENT, [ERROR], FakeLLM(error=ModelDeclined("refused")))
    empty = ask(INCIDENT, [], FakeLLM(answer("timeout", "E1")))

    assert declined.category == "unknown"
    assert empty.reason == "no symptoms were found"


def result(expected, got, outcome="diagnose"):
    return ProbeResult(
        incident_id="BENCH-0001",
        family="f",
        expected_outcome=outcome,
        expected_category=expected,
        answered=got,
        category=got,
        correct=got == expected,
        failure=None,
        cited=[],
        reason=None,
        shown=1,
        problems=[],
        seconds=1.0,
    )


def test_score_counts_right_wrong_and_abstentions():
    results = [
        result("timeout", "timeout"),
        result("timeout", "networking"),
        result("timeout", "unknown"),
        result("unknown", "unknown", "abstain"),
        result("unknown", "timeout", "abstain"),
    ]

    assert score(results) == Score(
        right=1, wrong=1, to_diagnose=3, abstained_rightly=1, to_abstain=2
    )


def test_the_probe_passes_at_exactly_the_marks():
    passed, lines = judge(Score(90, 5, 100, 9, 10))

    assert passed is True
    assert all(line.startswith("pass: ") for line in lines)


def test_89_right_or_8_abstentions_fail():
    assert judge(Score(89, 5, 100, 10, 10))[0] is False
    assert judge(Score(95, 5, 100, 8, 10))[0] is False


def test_a_run_of_another_size_is_not_judged():
    passed, lines = judge(Score(20, 0, 20, 2, 2))

    assert passed is None
    assert lines[0].startswith("not judged")
