"""The kind check: a subagent tests each fault of the lead's draft. No model is called."""

import json
from typing import Any

import pytest

pytest.importorskip("pyarrow")
pytest.importorskip("duckdb")

from flowguard.llm.claude import claude_schema  # noqa: E402
from flowguard.openrca2.baseline import (  # noqa: E402
    agent_contract,
    agents,
    investigate,
)
from flowguard.openrca2.chat import ModelFailed, ToolCall, Turn, Usage  # noqa: E402
from flowguard.openrca2.design import DATA  # noqa: E402
from flowguard.openrca2.failures import kind_checks  # noqa: E402
from flowguard.openrca2.subagents import (  # noqa: E402
    KIND_SYSTEM,
    VERDICT_SCHEMA,
    KindCheck,
    Verdict,
    kind_rules,
    review,
)


def answer(kind: str, service: str = "a") -> str:
    evidence = [{"kind": "trace", "sql": "SELECT 1", "claim": "x"}]
    fault = {"service": service, "fault_kind": kind, "evidence": evidence}
    return json.dumps({"root_causes": [fault], "propagation": []})


def finding(kind: str, confidence: str = "high") -> str:
    return json.dumps(
        {
            "scope": "every call on the connection to the database",
            "ruled_out": [{"kind": "database_call_slow", "why": "all statements slow"}],
            "kind": kind,
            "confidence": confidence,
            "evidence": [{"sql": "SELECT 2", "claim": "y"}],
        }
    )


class Scripted:
    """Plays back tool-calling turns, then one answer for each time it is asked to conclude."""

    def __init__(self, turns: int, answers: list[str], fail: bool = False) -> None:
        self.turns, self.answers, self.fail = turns, answers, fail
        self.prompts: list[tuple[str | None, str, Any]] = []
        self.spent = 0.0

    def ask(self) -> Turn:
        if self.fail:
            self.spent += 0.03
            raise ModelFailed("overloaded")
        calls = []
        if self.turns:
            self.turns -= 1
            calls = [ToolCall("t", "think_tool", {"reflection": "r"})]
        return Turn("", calls, Usage(prompt=100, output=10, usd=0.01), "end_turn")

    def answer_tools(self, results: list[tuple[ToolCall, str]]) -> None:
        pass

    def conclude(self, system: str | None, prompt: str, schema: Any = None) -> Turn:
        self.prompts.append((system, prompt, schema))
        return Turn(
            self.answers.pop(0), [], Usage(prompt=200, output=50, usd=0.02), "end_turn"
        )

    def transcript(self) -> list[dict[str, Any]]:
        return [{"role": "user", "content": "x"}]


class Tools:
    def run(self, call: ToolCall) -> str:
        return "ok"


def check(sub: Scripted, spawned: list[tuple[str, str]] | None = None) -> KindCheck:
    def spawn(system: str, first: str) -> Scripted:
        if spawned is not None:
            spawned.append((system, first))
        return sub

    return KindCheck(
        spawn, Tools().run, DATA, kind_rules(agent_contract()), "the survey text"
    )


def run(lead: Scripted, sub: Scripted, **more: Any) -> Any:
    tools: Any = Tools()
    agent = agents()["lead+survey+kind"]
    return investigate(lead, tools, agent=agent, kind_check=check(sub), **more)


def test_a_disagreeing_check_goes_back_to_the_lead_which_answers_again() -> None:
    lead = Scripted(1, [answer("database_call_slow"), answer("network_loss")])
    sub = Scripted(2, [finding("network_loss")])
    result = run(lead, sub)
    assert result.answer.root_causes[0].kind == "network_loss"
    assert (
        json.loads(result.draft)["root_causes"][0]["fault_kind"] == "database_call_slow"
    )
    assert len(lead.prompts) == 2
    shown = lead.prompts[1][1]
    assert "you said `database_call_slow`. They conclude `network_loss`" in shown
    assert "all statements slow" in shown and "`SELECT 2`" in shown
    # The lead's own turns (2 + 2 answers), not the subagent's.
    assert result.turns == 4 and len(result.per_turn) == 4
    # Lead: 2 x 0.01 + 2 x 0.02. Subagent: 3 x 0.01 + 0.02.
    assert result.usage.usd == pytest.approx(0.11)
    verdict = result.verdicts[0]
    assert verdict.disagrees and verdict.calls == 2 and verdict.turns == 4
    assert verdict.usage.usd == pytest.approx(0.05)
    assert verdict.record()["disagrees"] is True and verdict.record()["transcript"]


def test_an_agreeing_check_leaves_the_draft_as_the_answer() -> None:
    lead = Scripted(0, [answer("network_partition")])
    # Loss and partition are scored as the same answer, so this is agreement.
    result = run(lead, Scripted(0, [finding("network_loss")]))
    assert len(lead.prompts) == 1 and result.raw == result.draft
    assert not result.verdicts[0].disagrees


def test_a_failed_check_does_not_lose_the_case() -> None:
    lead = Scripted(0, [answer("http_slow")])
    result = run(lead, Scripted(0, [], fail=True))
    assert result.answer.root_causes[0].kind == "http_slow" and len(lead.prompts) == 1
    verdict = result.verdicts[0]
    assert verdict.kind is None and not verdict.disagrees
    assert "the kind check failed: overloaded" in verdict.notes
    assert result.usage.usd == pytest.approx(
        0.02 + 0.01 + 0.03
    )  # what it cost is counted


def test_an_unusable_finding_or_second_answer_keeps_the_draft() -> None:
    lead = Scripted(0, [answer("http_slow")])
    result = run(lead, Scripted(0, ['{"kind": "gremlins"}']))
    assert result.verdicts[0].kind is None and result.raw == result.draft

    lead = Scripted(0, [answer("http_slow"), "I changed my mind."])
    result = run(lead, Scripted(0, [finding("network_delay")]))
    assert result.answer.root_causes[0].kind == "http_slow"
    assert (
        "the answer after the kind check was invalid; the draft stands" in result.notes
    )


def test_an_invalid_draft_is_not_checked() -> None:
    result = run(Scripted(0, ["no answer"]), Scripted(0, []))
    assert result.answer is None and result.draft is None and result.verdicts == []


def test_only_the_first_faults_of_a_draft_are_checked() -> None:
    faults = json.loads(answer("pod_failure"))["root_causes"] * 5
    lead = Scripted(0, [json.dumps({"root_causes": faults, "propagation": []})])
    sub = Scripted(0, [finding("pod_failure")] * 5)
    assert len(run(lead, sub).verdicts) == 3


def test_the_subagent_stops_at_the_spending_limit() -> None:
    lead = Scripted(0, [answer("pod_failure")])
    # The lead's answer cost 0.03; the limit is passed after the subagent's first turn.
    result = run(
        lead, Scripted(9, [finding("pod_failure")]), budget=lambda usd: usd < 0.035
    )
    assert result.verdicts[0].calls == 1


def test_the_subagent_is_told_the_claim_the_rules_and_the_survey() -> None:
    spawned: list[tuple[str, str]] = []
    claim = json.loads(answer("database_call_slow", "ts-order-service"))["root_causes"][
        0
    ]
    check(Scripted(0, [finding("network_loss")]), spawned)(claim)
    system, first = spawned[0]
    assert "service `ts-order-service` suffered `database_call_slow`" in first
    assert "`SELECT 1`" in first and "the survey text" in first
    for words in (
        "try to disprove it",
        "Ten tables",
        "### Network (between services)",
        "## Equivalence classes",
        "find the scope",
        "the hard cap is 20",
    ):
        assert words in system
    # The answer format belongs to the lead, not the subagent.
    assert "## Output schema" not in system and "## Field rules" not in system
    assert "{" not in KIND_SYSTEM.replace("{data}", "").replace("{rules}", "").replace(
        "{max_calls}", ""
    )


def test_the_finding_is_held_to_a_strict_schema_with_the_reasoning_first() -> None:
    sub = Scripted(0, [finding("network_loss")])
    check(sub)({"service": "a", "fault_kind": "http_slow", "evidence": []})
    assert sub.prompts[0][0] is None and sub.prompts[0][2] is VERDICT_SCHEMA
    assert list(VERDICT_SCHEMA["properties"])[:3] == ["scope", "ruled_out", "kind"]
    sent = claude_schema(VERDICT_SCHEMA)
    assert sent["additionalProperties"] is False
    assert sent["properties"]["ruled_out"]["items"]["additionalProperties"] is False
    assert sent["properties"]["evidence"]["items"]["additionalProperties"] is False
    assert "pod_failure" in sent["properties"]["kind"]["enum"]


def test_the_review_reports_agreement_and_missing_findings_too() -> None:
    agreed = Verdict("a", "pod_failure", "pod_unavailable", "high", "all of a")
    text = review([agreed, Verdict("b", "http_slow")])
    assert "`a`: you said `pod_failure`. They agree (confidence: high)." in text
    assert "`b`: you said `http_slow`. The check gave no finding." in text
    assert "You may keep your draft or change it." in text


def test_the_other_agents_have_no_kind_check() -> None:
    assert [name for name, a in agents().items() if a.kind_check] == [
        "lead+survey+kind"
    ]
    lead, kind = agents()["lead+survey"], agents()["lead+survey+kind"]
    # Same lead: only the check differs, so a change in score is the check's.
    assert lead.system == kind.system and lead.answer_prompt == kind.answer_prompt


def test_the_report_shows_what_the_checks_did_to_the_answers() -> None:
    def record(disagrees: bool, draft: int, final: int) -> dict[str, Any]:
        return {
            "kind_checks": [{"disagrees": disagrees, "kind": "http_slow"}],
            "draft_scores": {"acc": draft},
            "scores": {"acc": final},
            "usage_kind_checks": 0.01,
        }

    records = [
        record(True, 0, 1),
        record(True, 0, 1),
        record(True, 1, 0),
        record(False, 1, 1),
    ]
    text = chr(10).join(kind_checks("run", [*records, {"scores": {"acc": 1}}]))
    assert "on 4 cases with a valid draft" in text
    assert "2 for the drafts, 3 for the final answers. The checks cost $0.04." in text
    assert "| a check disagreed | wrong | right | 2 |" in text
    assert "| a check disagreed | right | wrong | 1 |" in text
    assert "| every check agreed | right | right | 1 |" in text
    assert kind_checks("run", [{"scores": {"acc": 1}}]) == []
