"""The explain path: read the symptoms, then ask which change explains them."""

import json
import re
from datetime import UTC, datetime

import pytest
from test_investigation_graph import (
    REQUEST,
    SPEC,
    FakeAudit,
    FakeRetriever,
    full_tools,
    new_graph,
)

from flowguard.domain.evidence import EvidenceItem
from flowguard.domain.incidents import Incident
from flowguard.graph.builder import investigate
from flowguard.graph.context import Dependencies
from flowguard.graph.nodes.explain import (
    NO_CHANGE_NEEDED,
    UNEXPLAINED,
    InvalidAnswer,
    diagnose,
)

INCIDENT = Incident(
    incident_id="BENCH-0001",
    description="Exports to the partner aren't acknowledged since about 13:00.",
    affected_system="billing",
    start_time=datetime(2027, 2, 9, 12, tzinfo=UTC),
    end_time=datetime(2027, 2, 9, 15, tzinfo=UTC),
)


def item(evidence_id, source_type, content, level=None):
    return EvidenceItem(
        evidence_id=evidence_id,
        source_type=source_type,
        source_name="billing-exporter",
        timestamp=datetime(2027, 2, 9, 13, tzinfo=UTC)
        if source_type == "log"
        else None,
        title=f"{source_type} title",
        content=content,
        metadata={"level": level} if level else {},
    )


ERROR = item("LOG-00089", "log", "No acknowledgement from the partner in 60 s", "ERROR")
SPEC_ITEM = item("SPEC-00012#delivery", "api_spec", "Files go to /inbound.")
RUNBOOK = item("RB-00013", "runbook", "Check the upload directory.")
CHANGE = item("DEPLOY-BILLING-00084", "deployment", "Upload to /outbound instead")
EVIDENCE = [ERROR, SPEC_ITEM, RUNBOOK, CHANGE]


def ids_of(prompt, kind):
    """The neutral IDs the prompt gives evidence of one kind."""
    return re.findall(rf"ID: (E\d+)\nType: {kind}", prompt)


class Script:
    """Answers each question from what its prompt shows, and records the questions."""

    def __init__(self, read, explain=None, actions=None):
        self.read = read
        self.explain = explain
        self.actions = actions or []
        self.calls = []

    def generate(self, system, prompt, schema):
        self.calls.append((system, prompt, schema))
        fields = schema.get("properties", {})
        if "pattern" in fields:
            return json.dumps(self.read(prompt))
        if "explained_by" in fields:
            return json.dumps(self.explain(prompt))
        return json.dumps({"actions": self.actions(prompt) if self.actions else []})


def reading(category="timeout", pattern="sustained", kind="log"):
    return lambda prompt: {
        "failure": "Uploads aren't acknowledged.",
        "evidence_ids": ids_of(prompt, kind),
        "pattern": pattern,
        "category": category,
    }


def explanation(by, category="timeout"):
    def answer(prompt):
        chosen = ids_of(prompt, "deployment")[0] if by == "change" else by
        return {
            "explanation": "The release changed the upload directory.",
            "explained_by": chosen,
            "evidence_ids": ids_of(prompt, "log"),
            "category": category,
        }

    return answer


def test_the_first_question_shows_only_symptoms_with_neutral_ids():
    llm = Script(reading(), explanation(NO_CHANGE_NEEDED))

    diagnose(INCIDENT, EVIDENCE, llm)

    _, prompt, schema = llm.calls[0]
    assert "Type: log (ERROR)" in prompt and "Type: api_spec" in prompt
    assert "deployment" not in prompt and "runbook" not in prompt
    for original in ("LOG-00089", "SPEC-00012", "DEPLOY-BILLING-00084"):
        assert original not in prompt
    assert schema["properties"]["evidence_ids"]["items"]["enum"] == ["E1", "E2"]


def test_the_second_question_shows_the_reading_and_the_changes():
    llm = Script(reading(), explanation(NO_CHANGE_NEEDED))

    diagnose(INCIDENT, EVIDENCE, llm)

    _, prompt, schema = llm.calls[1]
    assert "<reading>\nWhat failed: Uploads aren't acknowledged." in prompt
    assert "Type: deployment" in prompt and "Type: runbook" in prompt
    assert schema["properties"]["explained_by"]["enum"] == [
        "E4",
        NO_CHANGE_NEEDED,
        UNEXPLAINED,
    ]


def test_an_isolated_problem_is_not_diagnosed_and_not_explained():
    llm = Script(reading(pattern="isolated"))

    result = diagnose(INCIDENT, EVIDENCE, llm)

    assert result.category == "unknown"
    assert "isolated" in result.abstention
    assert result.read_as == "timeout"
    assert len(llm.calls) == 1


def test_a_reading_that_cites_no_log_or_no_category_is_not_diagnosed():
    no_log = diagnose(INCIDENT, EVIDENCE, Script(reading(kind="api_spec")))
    no_category = diagnose(INCIDENT, EVIDENCE, Script(reading(category="unknown")))

    assert no_log.abstention == "the reading of the symptoms cites no log"
    assert no_category.category == "unknown"


def test_an_unexplained_failure_is_not_diagnosed():
    result = diagnose(INCIDENT, EVIDENCE, Script(reading(), explanation(UNEXPLAINED)))

    assert result.category == "unknown"
    assert result.abstention == "nothing in the evidence explains the failure"


def test_a_failure_that_needs_no_change_keeps_what_the_symptoms_showed():
    result = diagnose(
        INCIDENT, EVIDENCE, Script(reading(), explanation(NO_CHANGE_NEEDED))
    )

    assert result.category == "timeout"
    assert result.abstention is None
    assert "DEPLOY-BILLING-00084" not in result.supporting


def test_a_change_that_explains_the_failure_is_cited_and_may_correct_it():
    result = diagnose(
        INCIDENT,
        EVIDENCE,
        Script(reading(), explanation("change", category="file_transfer")),
    )

    assert result.category == "file_transfer"
    assert result.supporting == ("LOG-00089", "DEPLOY-BILLING-00084")
    # The record names the change by its original ID, not the question's.
    assert result.notes == (
        "explained by: DEPLOY-BILLING-00084",
        "the change explains it: timeout became file_transfer",
    )


def test_the_change_can_never_turn_the_answer_into_the_release():
    result = diagnose(
        INCIDENT,
        EVIDENCE,
        Script(
            reading(), explanation("change", category="deployment_or_configuration")
        ),
    )

    assert result.category == "timeout"


def test_without_logs_nothing_is_asked():
    llm = Script(reading())

    result = diagnose(INCIDENT, [SPEC_ITEM, CHANGE], llm)

    assert result.category == "unknown"
    assert llm.calls == []


def test_a_broken_or_invented_answer_is_refused():
    class Broken(Script):
        def generate(self, system, prompt, schema):
            return "not json"

    with pytest.raises(InvalidAnswer):
        diagnose(INCIDENT, EVIDENCE, Broken(reading()))
    invented = Script(reading(), explanation("E99"))
    with pytest.raises(InvalidAnswer):
        diagnose(INCIDENT, EVIDENCE, invented)


# --------------------------------------------------------- through the real graph


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def run(llm, audit=None):
    tools = full_tools()
    tools.retriever = FakeRetriever(SPEC)
    return await investigate(
        new_graph(),
        REQUEST,
        Dependencies(
            tools=tools, llm=llm, audit=audit or FakeAudit(), diagnosis="explain"
        ),
        investigation_id="INVEST-1",
    )


def rollback(prompt):
    # The remediation question cites evidence by its original ID.
    return [
        {
            "action": "rollback_deployment",
            "target": "DEPLOY-SOURCE-221",
            "reason": "The release explains the failure.",
            "evidence_ids": ["DEPLOY-SOURCE-221"],
        }
    ]


@pytest.mark.anyio
async def test_the_graph_diagnoses_and_plans_from_an_explaining_change():
    audit = FakeAudit()
    llm = Script(
        reading("schema_contract_mismatch"),
        explanation("change", category="schema_contract_mismatch"),
        rollback,
    )

    state = await run(llm, audit)

    assert state["category"] == "schema_contract_mismatch"
    assert state["decision_rule"] == "explain"
    assert "DEPLOY-SOURCE-221" in state["selected_root_cause"].supporting_evidence_ids
    assert [a.action for a in state["actions"]] == ["rollback_deployment"]
    assert audit.records[-1].decision_rule == "explain"


@pytest.mark.anyio
async def test_the_graph_abstains_on_an_isolated_problem():
    state = await run(Script(reading("networking", pattern="isolated")))

    assert state["category"] == "unknown"
    assert state["status"] == "abstained"
    assert "isolated" in state["abstention"]


def test_the_explain_path_is_the_default():
    # Chosen on 2026-11-11 after the benchmark-2031 test run (brief, section 14).
    assert (
        Dependencies(
            tools=full_tools(), llm=Script(reading()), audit=FakeAudit()
        ).diagnosis
        == "explain"
    )
