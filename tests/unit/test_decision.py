from dataclasses import dataclass

import pytest

from flowguard.domain.decision import FIT_BONUS, decide, shared_support


@dataclass(frozen=True)
class H:
    category: str
    support: float | None
    proposed_rank: int | None = None
    signals: tuple[str, ...] = ()
    fit: float | None = None
    verdict: str | None = None
    contradicting_evidence_ids: tuple[str, ...] = ()


RELEASE = ("timeline", "dependency_path", "deployment")


def test_the_rubric_abstains_on_one_hypothesis_s_score_whatever_the_evidence():
    decision = decide("rubric", [H("timeout", 0.45)], evidence_score=0.9)

    assert decision.selected is None
    assert decision.abstention == "the best hypothesis scored 0.45, below 0.65"


@pytest.mark.parametrize("rule", ["evidence", "evidence_shared", "model", "checked"])
def test_the_other_rules_abstain_on_the_evidence_together(rule):
    # A right answer that lost points for listing contradicting evidence.
    candid = H("rate_limiting", 0.45, proposed_rank=1, signals=("error_log",))

    assert decide(rule, [candid], evidence_score=0.85).selected == candid
    weak = decide(rule, [candid], evidence_score=0.55)
    assert weak.selected is None
    assert weak.abstention == "the evidence together scored 0.55, below 0.65"


def test_without_an_evidence_score_every_rule_falls_back_to_the_rubric_gate():
    # Records from before the evidence score was kept.
    assert (
        decide("evidence", [H("timeout", 0.45)], evidence_score=None).selected is None
    )


def test_the_fit_bonus_goes_to_the_category_that_best_matches_the_logs():
    release = H("deployment_or_configuration", 0.75, fit=0.40)
    quota = H("rate_limiting", 0.60, fit=0.70)

    assert decide("rubric", [release, quota], 0.9).selected == release
    assert decide("evidence", [release, quota], 0.9).selected == quota
    assert 0.60 + FIT_BONUS > 0.75


def test_shared_credit_stops_a_release_winning_by_citing_it_alone():
    release = H("deployment_or_configuration", 0.45, signals=RELEASE)
    logs = H("networking", 0.30, signals=("error_log",))

    assert shared_support(logs, [release, logs], 0) == 0.75
    assert shared_support(release, [release, logs], 0) == 0.45
    assert decide("evidence_shared", [release, logs], 0.75).selected == logs
    assert decide("evidence", [release, logs], 0.75).selected == release


def test_shared_credit_keeps_the_deductions():
    contradicted = H(
        "networking", 0.0, signals=("error_log",), contradicting_evidence_ids=("A", "B")
    )

    assert shared_support(contradicted, [contradicted], missing_sources=1) == 0.0


def test_the_model_rule_takes_the_model_s_first_choice():
    first = H("timeout", 0.40, proposed_rank=1)
    second = H("deployment_or_configuration", 0.85, proposed_rank=2)

    assert decide("model", [second, first], 0.9).selected == first


def test_the_check_puts_what_failed_above_what_came_before():
    trigger = H("deployment_or_configuration", 0.85, verdict="trigger_only")
    mechanism = H("timeout", 0.45, verdict="mechanism")

    decision = decide("checked", [trigger, mechanism], 0.9)

    assert decision.ranked == (mechanism, trigger)


def test_the_check_rules_out_what_the_evidence_does_not_show():
    unsupported = H("authorisation", 0.9, verdict="not_supported")
    supported = H("rate_limiting", 0.5, verdict="trigger_only")

    decision = decide("checked", [unsupported, supported], 0.9)

    assert decision.selected == supported
    assert decision.ranked[-1] == unsupported


def test_the_check_abstains_when_it_rules_everything_out():
    decision = decide("checked", [H("timeout", 0.9, verdict="not_supported")], 0.9)

    assert decision.selected is None
    assert decision.abstention == "the check found no hypothesis the evidence supports"


def test_without_verdicts_the_checked_rule_is_the_evidence_rule():
    hypotheses = [H("timeout", 0.6, fit=0.2), H("networking", 0.5, fit=0.6)]

    assert decide("checked", hypotheses, 0.9) == decide("evidence", hypotheses, 0.9)


def test_no_hypotheses_means_no_decision():
    assert decide("evidence", [], 0.9).abstention == "no hypothesis was proposed"
