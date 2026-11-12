"""Signals from counted log patterns, and the explain path's rules that use them."""

from datetime import UTC, datetime

import pytest
from test_explain import EVIDENCE, INCIDENT, Script, explanation, reading
from test_investigation_graph import REQUEST, FakeAudit, FakeTools, new_graph

from flowguard.domain.evidence import EvidenceItem
from flowguard.domain.setup import CHANGE_KINDS, SetupProfile
from flowguard.domain.signals import candidates, deepest, describe, kind_of
from flowguard.graph.builder import investigate
from flowguard.graph.context import Dependencies
from flowguard.graph.nodes.explain import (
    EXPLAIN_SYSTEM,
    NO_CHANGE_NEEDED,
    READ_SYSTEM,
    UNEXPLAINED,
    diagnose,
)

NOTHING_RECORDED = SetupProfile(recorded_changes=())


def log(evidence_id, service, level, before, after):
    return EvidenceItem(
        evidence_id=evidence_id,
        source_type="log",
        source_name=service,
        # Inside the window of the graph tests' request.
        timestamp=datetime(2026, 4, 2, 9, 15, tzinfo=UTC),
        title=f"{level} event",
        content=f"{service} said something",
        metadata={
            "level": level,
            "count_before": before,
            "count_after": after,
            "minutes_before": 5,
            "minutes_after": 10,
        },
    )


# The same error all day: 46 a minute before, 37 a minute since.
QUEUE = log("LOG-1", "queue-master", "ERROR", 231, 369)
CARTS = log("LOG-2", "carts", "ERROR", 0, 12)
FRONT = log("LOG-3", "front-end", "ERROR", 0, 148)
SLOW = log("LOG-4", "carts", "WARN", 2, 30)
GONE = log("LOG-5", "orders", "ERROR", 4, 0)
CHATTY = log("LOG-6", "user", "INFO", 0, 9)
MAP = EvidenceItem(
    evidence_id="DEPMAP-SHOP",
    source_type="dependency_map",
    source_name="shop",
    title="shop dependency map",
    content="carts -> front-end",
    metadata={
        "nodes": [],
        # An edge from A to B means B depends on A.
        "edges": [
            {"from": "carts", "to": "front-end"},
            {"from": "carts-db", "to": "carts"},
            {"from": "rabbitmq", "to": "queue-master"},
        ],
    },
)
COUNTED = [QUEUE, FRONT, CARTS, SLOW, GONE, CHATTY, MAP]


def test_each_pattern_is_new_increased_steady_or_stopped():
    assert [kind_of(i) for i in (CARTS, SLOW, QUEUE, GONE)] == [
        "new",
        "increased",
        "steady",
        "stopped",
    ]
    assert kind_of(EVIDENCE[0]) is None
    assert kind_of(MAP) is None


def test_the_signal_is_worded_for_the_model():
    assert describe(QUEUE) == (
        "background, about as frequent before the failure began: "
        "231 times in the 5 minutes before, 369 times in the 10 minutes since"
    )
    assert describe(CARTS).startswith("new since the failure began: 12 times")
    assert describe(EVIDENCE[0]) is None


def test_candidates_have_a_new_or_increased_problem_deepest_first():
    # queue-master's error is background, orders' stopped, and user's is not an
    # error; front-end depends on carts, so carts comes first.
    assert candidates(COUNTED) == ["carts", "front-end"]
    assert deepest(COUNTED) == ["carts"]
    assert candidates([QUEUE, MAP]) == []


def test_logs_without_counts_have_no_candidates_to_offer():
    assert candidates(EVIDENCE) is None
    assert deepest(EVIDENCE) == []


def test_with_signals_the_model_is_told_them_and_chooses_among_candidates():
    llm = Script(reading(), explanation(NO_CHANGE_NEEDED, service="carts"))

    result = diagnose(INCIDENT, COUNTED, llm)

    (read_system, read_prompt, _), (system, prompt, schema) = llm.calls
    assert read_system.startswith(READ_SYSTEM) and "Signal line" in read_system
    assert "Signal: background, about as frequent" in read_prompt
    assert system.startswith(EXPLAIN_SYSTEM) and "<candidates>" in system
    assert "<candidates>\ncarts\nfront-end (depends on carts)\n</candidates>" in prompt
    assert schema["properties"]["service"]["enum"] == ["carts", "front-end"]
    assert (result.category, result.service) == ("timeout", "carts")


def test_without_signals_the_questions_are_exactly_as_before():
    llm = Script(reading(), explanation(NO_CHANGE_NEEDED))

    diagnose(INCIDENT, EVIDENCE, llm, NOTHING_RECORDED)

    (read_system, read_prompt, _), (system, prompt, _) = llm.calls
    assert (read_system, system) == (READ_SYSTEM, EXPLAIN_SYSTEM)
    assert "Signal:" not in read_prompt + prompt
    assert "<candidates>" not in prompt


def test_a_service_whose_errors_were_already_there_is_refused():
    llm = Script(reading(), explanation(NO_CHANGE_NEEDED, service="queue-master"))

    result = diagnose(INCIDENT, COUNTED, llm, NOTHING_RECORDED)

    assert result.category == "unknown"
    assert result.abstention == "the named service shows no new or increased error"
    assert result.service is None and not result.located
    assert "named: queue-master" in result.notes


def test_when_nothing_is_new_nothing_is_asked():
    llm = Script(reading())

    result = diagnose(INCIDENT, [QUEUE, GONE, MAP], llm)

    assert "no service shows a new or increased error" in result.abstention
    assert llm.calls == []


def test_an_unexplained_failure_is_located_where_changes_arent_recorded():
    answers = reading(), explanation(UNEXPLAINED, service="carts")

    located = diagnose(INCIDENT, COUNTED, Script(*answers), NOTHING_RECORDED)
    recorded = diagnose(INCIDENT, COUNTED, Script(*answers), SetupProfile())

    assert located.located and located.service == "carts"
    assert located.category == "unknown"
    assert located.abstention.startswith("located in carts, but nothing recorded")
    assert "deployment, configuration" in located.abstention
    # Where every kind of change is recorded, "nothing explains it" stands.
    assert not recorded.located
    assert recorded.abstention == "nothing in the evidence explains the failure"


def test_a_setup_that_records_some_kinds_of_change_can_still_locate():
    profile = SetupProfile(recorded_changes=("deployment",))

    result = diagnose(
        INCIDENT,
        COUNTED,
        Script(reading(), explanation(UNEXPLAINED, service="carts")),
        profile,
    )

    assert result.located
    assert result.abstention.endswith("configuration, feature_flag, migration")
    assert SetupProfile().recorded_changes == CHANGE_KINDS


def test_a_failure_with_no_category_can_be_located_but_not_diagnosed():
    answers = (
        reading(category="unknown"),
        explanation(NO_CHANGE_NEEDED, category="unknown", service="front-end"),
    )
    asked = Script(*answers)
    not_asked = Script(*answers)

    located = diagnose(INCIDENT, COUNTED, asked, NOTHING_RECORDED)
    abstained = diagnose(INCIDENT, COUNTED, not_asked, SetupProfile())

    assert located.located and located.service == "front-end"
    assert len(asked.calls) == 2
    assert not abstained.located and len(not_asked.calls) == 1


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_the_graph_records_a_located_failure_and_plans_nothing():
    audit = FakeAudit()

    state = await investigate(
        new_graph(),
        REQUEST,
        Dependencies(
            tools=FakeTools((QUEUE, FRONT, CARTS), (), (MAP,)),
            llm=Script(reading(), explanation(UNEXPLAINED, service="carts")),
            audit=audit,
            profile=NOTHING_RECORDED,
        ),
        investigation_id="INVEST-1",
    )

    assert state["status"] == "abstained"
    assert state["located"] and state["root_cause_service"] == "carts"
    assert state["abstention"].startswith("located in carts")
    assert not state.get("actions")
    assert audit.records[-1].located
    assert audit.records[-1].root_cause_service == "carts"
