"""The kind and spread checks: subagents test each fault of the lead's draft. No model is called."""

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
from flowguard.openrca2.failures import edge_f1, kind_checks  # noqa: E402
from flowguard.openrca2.subagents import (  # noqa: E402
    KIND_SYSTEM,
    SPREAD_SCHEMA,
    VERDICT_SCHEMA,
    KindCheck,
    Spread,
    SpreadCheck,
    Verdict,
    changes_edges,
    kind_rules,
    link_table,
    propagation_rules,
    review,
    review_all,
    routes,
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
    assert "the answer after the checks was invalid; the draft stands" in result.notes


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
    checked = {n: (a.kind_check, a.spread_check) for n, a in agents().items()}
    assert checked == {
        "standard": (False, False),
        "lead": (False, False),
        "lead+survey": (False, False),
        "lead+survey+kind": (True, False),
        "lead+survey+spread": (False, True),
        "lead+survey+kind+spread": (True, True),
    }
    # Same lead: only the checks differ, so a change in score is the checks'.
    base = agents()["lead+survey"]
    for name in ("lead+survey+kind", "lead+survey+spread", "lead+survey+kind+spread"):
        other = agents()[name]
        assert (other.system, other.answer_prompt) == (base.system, base.answer_prompt)


def test_the_kind_check_alone_sends_the_review_it_was_first_measured_with() -> None:
    lead = Scripted(0, [answer("database_call_slow"), answer("network_loss")])
    run(lead, Scripted(0, [finding("network_loss")]))
    assert lead.prompts[1][1].startswith("A second investigator, starting fresh")


def test_the_report_shows_what_the_checks_did_to_the_answers() -> None:
    def record(disagrees: bool, draft: int, final: int) -> dict[str, Any]:
        # As the kind-check run records it: no `second_answer` field.
        return {
            "kind_checks": [{"disagrees": disagrees, "kind": "http_slow"}],
            "draft_scores": {"acc": draft, "edge_f1": 0.5},
            "scores": {"acc": final, "edge_f1": 0.5},
            "usage_kind_checks": 0.01,
        }

    spread_only = {
        "second_answer": True,
        "draft_scores": {"acc": 1, "edge_f1": 0.5},
        "scores": {"acc": 1, "edge_f1": 1.0},
        "usage_spread_checks": 0.02,
    }
    records = [
        record(True, 0, 1),
        record(True, 0, 1),
        record(True, 1, 0),
        record(False, 1, 1),
        spread_only,
    ]
    text = chr(10).join(kind_checks("run", [*records, {"scores": {"acc": 1}}]))
    assert "on 5 cases with a valid draft" in text
    assert "3 for the drafts, 4 for the final answers." in text
    assert "Edge-F1: 0.500 for the drafts, 0.600 for the final answers." in text
    assert "The checks cost $0.06." in text
    assert "| the lead answered again | wrong | right | 2 |" in text
    assert "| the lead answered again | right | wrong | 1 |" in text
    assert "| the lead answered again | right | right | 1 |" in text
    assert "| the draft stood | right | right | 1 |" in text
    assert kind_checks("run", [{"scores": {"acc": 1}}]) == []
    assert edge_f1([{"edge_f1": None}, {"edge_f1": 0.5}, {}]) == 0.5


# The spread check -------------------------------------------------------------

LINKS = [
    # (caller, callee, rate n, a, errors n, a, p95 n, a), as survey.calls gives them
    ("frontend", "search", 60.0, 60.0, 0.0, 0.5, 10.0, 900.0),
    ("search", "rate", 60.0, 60.0, 0.0, 0.0, 5.0, 5.0),
    ("search", "geo", 60.0, 60.0, 0.0, 0.0, 5.0, 5.0),
    ("ui", "plan", 30.0, 30.0, 0.0, 0.4, 10.0, 500.0),
    ("ui", "travel", 30.0, 30.0, 0.0, 0.4, 10.0, 500.0),
    ("plan", "route", 30.0, 30.0, 0.0, 0.4, 10.0, 500.0),
    ("route", "travel", 30.0, 30.0, 0.0, 0.4, 10.0, 500.0),
    ("loadgen-entry", "ui", 1.0, 1.0, 0.0, 0.0, 1.0, 1.0),
    ("other", "unrelated", 1.0, 1.0, 0.0, 0.0, 1.0, 1.0),
]


def edge_answer(kind: str, service: str, edges: list[tuple[str, str]]) -> str:
    data = json.loads(answer(kind, service))
    evidence = [{"kind": "trace", "sql": "SELECT 1", "claim": "x"}]
    data["propagation"] = [{"from": a, "to": b, "evidence": evidence} for a, b in edges]
    return json.dumps(data)


def traced(edges: list[tuple[str, str]], reaches: bool = True) -> str:
    return json.dumps(
        {
            "reasoning": "two routes to ui",
            "edges": [
                {"from": a, "to": b, "evidence": [{"sql": "SELECT 3", "claim": "z"}]}
                for a, b in edges
            ],
            "reaches_users": reaches,
        }
    )


def spread_check(
    sub: Scripted, spawned: list[tuple[str, str]] | None = None
) -> SpreadCheck:
    def spawn(system: str, first: str) -> Scripted:
        if spawned is not None:
            spawned.append((system, first))
        return sub

    return SpreadCheck(
        spawn,
        Tools().run,
        DATA,
        propagation_rules(agent_contract()),
        "the survey text",
        LINKS,
        ["ui", "frontend"],
    )


def test_routes_climb_every_caller_to_the_entries_and_add_the_callees() -> None:
    up = routes(LINKS, "travel", ["ui", "frontend"])
    assert {(a, b) for a, b, *_ in up} == {
        ("ui", "travel"),
        ("route", "travel"),
        ("plan", "route"),
        ("ui", "plan"),
    }  # both routes to ui; nothing beyond the entry, nothing unrelated
    down = routes(LINKS, "search", ["frontend"])
    assert [(a, b) for a, b, *_ in down][:2] == [("search", "rate"), ("search", "geo")]
    assert ("frontend", "search") in {(a, b) for a, b, *_ in down}
    table = link_table(down)
    assert "| From (called) | To (caller) |" in table
    assert "| search | frontend | 60.0 → 60.0 | 0.00 → 0.50 | 10.0 → 900.0 |" in table
    assert "No calls" in link_table([])


def test_the_spread_subagent_is_told_the_fault_the_routes_and_the_rules() -> None:
    spawned: list[tuple[str, str]] = []
    claim = json.loads(answer("network_delay", "travel"))["root_causes"][0]
    found = spread_check(Scripted(1, [traced([("travel", "ui")])]), spawned)(
        claim, [("travel", "route")]
    )
    system, first = spawned[0]
    assert "service `travel`, kind `network_delay`" in first
    assert "travel → route" in first and "Entry services" in first
    assert "| travel | ui |" in first and "the survey text" in first
    assert "FAULT-IMPACT chain" in system and "Synthetic traffic generators" in system
    assert "Follow every route" in system and "the hard cap is 20" in system
    assert "## SQL rules" not in system and "fault_kind enum" not in system
    assert found.edges is not None and found.pairs() == {("travel", "ui")}
    assert found.reaches_users and found.links_listed == 4 and found.calls == 1


def test_the_spread_finding_is_held_to_a_strict_schema_with_the_reasoning_first() -> (
    None
):
    assert list(SPREAD_SCHEMA["properties"])[0] == "reasoning"
    sent = claude_schema(SPREAD_SCHEMA)
    edge = sent["properties"]["edges"]["items"]
    assert (
        sent["additionalProperties"] is False and edge["additionalProperties"] is False
    )
    assert edge["properties"]["evidence"]["items"]["additionalProperties"] is False


def run_both(lead: Scripted, sub: Scripted, *, kind: bool = True) -> Any:
    tools: Any = Tools()
    name = "lead+survey+kind+spread" if kind else "lead+survey+spread"
    return investigate(
        lead,
        tools,
        agent=agents()[name],
        kind_check=check(sub) if kind else None,
        spread_check=spread_check(sub),
    )


def test_new_edges_send_the_draft_back_with_both_findings() -> None:
    draft = edge_answer(
        "network_delay", "travel", [("travel", "route"), ("route", "plan")]
    )
    final = edge_answer(
        "network_delay", "travel", [("travel", "ui"), ("travel", "route")]
    )
    lead = Scripted(0, [draft, final])
    # The kind check agrees; the spread check finds an edge the draft lacks.
    sub = Scripted(
        0, [finding("network_delay"), traced([("travel", "ui"), ("travel", "route")])]
    )
    result = run_both(lead, sub)
    assert result.second_answer and len(lead.prompts) == 2
    shown = lead.prompts[1][1]
    assert "you said `network_delay`. They agree" in shown
    assert "### How the effect of `travel` (`network_delay`) travelled" in shown
    assert "- travel → ui (not in your draft)" in shown
    assert "- travel → route\n" in shown
    assert (
        "Edges in your draft near this fault that they did not find: route → plan"
        in shown
    )
    assert "faults and edges alike" in shown
    assert result.answer.edges == (("travel", "ui"), ("travel", "route"))
    assert len(result.verdicts) == 1 and len(result.spreads) == 1


def test_the_same_edges_and_an_agreeing_kind_keep_the_draft() -> None:
    draft = edge_answer("network_delay", "travel", [("travel", "ui")])
    lead = Scripted(0, [draft])
    # Names differing only in case, hyphens or underscores are the same service.
    sub = Scripted(0, [finding("network_delay"), traced([("Travel", "u-i")])])
    result = run_both(lead, sub)
    assert not result.second_answer and len(lead.prompts) == 1 and result.raw == draft


def test_a_spread_check_alone_runs_without_a_kind_check() -> None:
    draft = edge_answer("pod_failure", "travel", [])
    lead = Scripted(
        0, [draft, edge_answer("pod_failure", "travel", [("travel", "ui")])]
    )
    result = run_both(
        lead, Scripted(0, [traced([("travel", "ui")], reaches=True)]), kind=False
    )
    assert result.verdicts == [] and result.second_answer
    assert "you said" not in lead.prompts[1][1]


def test_a_failed_or_unusable_spread_check_keeps_the_draft() -> None:
    draft = edge_answer("pod_failure", "travel", [("travel", "ui")])
    lead = Scripted(0, [draft])
    result = run_both(lead, Scripted(0, [], fail=True), kind=False)
    assert result.spreads[0].edges is None and not result.second_answer
    assert "the spread check failed: overloaded" in result.spreads[0].notes

    lead = Scripted(0, [draft])
    result = run_both(lead, Scripted(0, ['{"reasoning": "x"}']), kind=False)
    assert result.spreads[0].edges is None and not result.second_answer
    assert any("no usable finding" in n for n in result.spreads[0].notes)


def test_a_fault_that_did_not_reach_the_users_is_reported_as_such() -> None:
    text = review_all(
        [], [Spread("travel", "pod_failure", [], False, "stayed inside")], []
    )
    assert "its effect did not reach the entry services" in text
    assert not changes_edges([Spread("a", "b")], [("x", "y")])  # no finding: no change
    assert changes_edges([Spread("a", "b", [])], [("x", "y")])


def test_the_propagation_rules_are_the_contracts_own() -> None:
    rules = propagation_rules(agent_contract())
    assert rules.count("\n- ") + rules.startswith("- ") == 2
    assert "Do NOT use the request-call direction" in rules
    assert "never list them as `root_causes`" in rules
