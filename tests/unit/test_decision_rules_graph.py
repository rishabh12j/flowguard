"""The decision rules, the fit, and the check, run through the real graph."""

import pytest
from fakes import FakeLLM
from test_investigation_graph import (
    REQUEST,
    SPEC,
    FakeAudit,
    FakeRetriever,
    full_tools,
    new_graph,
    proposal,
)

from flowguard.graph.builder import investigate
from flowguard.graph.context import Dependencies

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def run(llm, audit=None, **settings):
    tools = full_tools()
    tools.retriever = FakeRetriever(SPEC)
    return await investigate(
        new_graph(),
        REQUEST,
        Dependencies(
            tools=tools,
            llm=llm,
            audit=audit or FakeAudit(),
            **{"diagnosis": "hypotheses", **settings},
        ),
        investigation_id="INVEST-1",
    )


# Right, but it lists a contradiction, so its own score falls below 0.65.
CANDID = proposal(
    "LOG-882",
    "DEPLOY-SOURCE-221",
    contradicting=(SPEC.evidence_id,),
    category="timeout",
)
# Wrong, but it cites everything, including the release.
RELEASE = proposal(
    "LOG-882",
    "DEPLOY-SOURCE-221",
    SPEC.evidence_id,
    category="deployment_or_configuration",
)


async def test_every_signal_is_recorded_for_re_scoring():
    audit = FakeAudit()

    state = await run(FakeLLM(CANDID, RELEASE), audit=audit)

    first, second = sorted(state["hypotheses"], key=lambda h: h.proposed_rank)
    assert (first.category, second.category) == (
        "timeout",
        "deployment_or_configuration",
    )
    assert set(second.signals) == {
        "error_log",
        "timeline",
        "dependency_path",
        "api_spec",
        "deployment",
    }
    assert state["evidence_score"] == 0.90
    assert state["decision_rule"] == "rubric"
    record = audit.records[-1]
    assert (record.evidence_score, record.decision_rule) == (0.90, "rubric")


async def test_the_evidence_rule_keeps_an_answer_the_rubric_abstains_on():
    llm = FakeLLM(CANDID)

    rubric = await run(llm)
    evidence = await run(FakeLLM(CANDID), rule="evidence")

    assert rubric["abstention"] == "the best hypothesis scored 0.55, below 0.65"
    assert evidence["selected_root_cause"].category == "timeout"


async def test_the_fit_is_recorded_and_can_decide_between_hypotheses():
    def fit(error_logs):
        assert error_logs, "the error logs are scored"
        return {"timeout": 0.8, "deployment_or_configuration": 0.3}

    state = await run(FakeLLM(CANDID, RELEASE), rule="evidence", fit=fit)

    fits = {h.category: h.fit for h in state["hypotheses"]}
    assert fits == {"timeout": 0.8, "deployment_or_configuration": 0.3}
    # 0.55 + 0.20 for the best fit doesn't beat 0.90: the bonus breaks near-ties only.
    assert state["selected_root_cause"].category == "deployment_or_configuration"


async def test_the_check_records_verdicts_and_the_checked_rule_uses_them():
    llm = FakeLLM(
        CANDID,
        RELEASE,
        verdicts=[
            {"hypothesis": 1, "verdict": "mechanism", "reason": "The query timed out."},
            {"hypothesis": 2, "verdict": "trigger_only", "reason": "It came first."},
        ],
    )

    state = await run(llm, rule="checked", check=True)

    verdicts = {h.category: h.verdict for h in state["hypotheses"]}
    assert verdicts == {
        "timeout": "mechanism",
        "deployment_or_configuration": "trigger_only",
    }
    assert state["selected_root_cause"].category == "timeout"
    assert any("verdicts" in schema.get("properties", {}) for _, _, schema in llm.calls)


async def test_the_check_is_not_called_unless_it_is_on():
    llm = FakeLLM(CANDID, verdicts=[])

    await run(llm, rule="checked")

    assert not any(
        "verdicts" in schema.get("properties", {}) for _, _, schema in llm.calls
    )


async def test_a_failed_check_is_recorded_and_the_evidence_rule_decides():
    state = await run(
        FakeLLM(CANDID, RELEASE, verdicts="not json"), rule="checked", check=True
    )

    assert any(
        error.startswith("root_cause: the check failed") for error in state["errors"]
    )
    assert all(h.verdict is None for h in state["hypotheses"])
    assert state["selected_root_cause"].category == "deployment_or_configuration"
