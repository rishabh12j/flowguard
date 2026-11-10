from flowguard.evaluation.confirm import Verdict, judge, render, used_live
from flowguard.evaluation.investigations import EvaluationReport
from flowguard.evaluation.rules import RuleScore


def score(diagnosed, wrong, abstained=10, to_diagnose=100, to_abstain=10):
    return RuleScore(
        rule="evidence",
        diagnosed=diagnosed,
        to_diagnose=to_diagnose,
        wrong=wrong,
        abstained_rightly=abstained,
        to_abstain=to_abstain,
        confidence_auroc=None,
        high_confidence_right=0,
        high_confidence=0,
    )


RUBRIC = score(80, 10)


def test_the_rule_passes_at_exactly_the_marks():
    verdict = judge("run", score(85, 11, abstained=9), RUBRIC)

    assert verdict.passed
    assert all(line.startswith("pass: ") for line in verdict.lines)


def test_four_more_diagnoses_is_not_enough():
    assert not judge("run", score(84, 10), RUBRIC).passed


def test_two_more_wrong_diagnoses_fail():
    assert not judge("run", score(90, 12), RUBRIC).passed


def test_eight_abstentions_of_ten_fail():
    verdict = judge("run", score(90, 10, abstained=8), RUBRIC)

    assert not verdict.passed
    assert verdict.lines[2].startswith("FAIL: abstained on 8 of 10")


def test_a_run_of_another_size_is_not_judged():
    verdict = judge("run", score(50, 2, to_diagnose=50), score(40, 2, to_diagnose=50))

    assert not verdict.passed
    assert verdict.lines[0].startswith("not judged")


def test_the_rule_must_have_run_live():
    def report(model):
        return EvaluationReport.model_construct(model=model, incidents=[])

    assert used_live(report("gemma4:12b, rule evidence"), "evidence")
    assert used_live(
        report("claude-sonnet-5-5, rule evidence, with the check"), "evidence"
    )
    assert not used_live(report("gemma4:12b"), "evidence")
    assert not used_live(report("gemma4:12b, rule evidence_shared"), "evidence")


def test_the_rule_must_pass_in_every_run():
    passed = Verdict("gemma", True, ())
    failed = Verdict("claude", False, ())

    assert render("evidence", [passed, passed], ["", ""]).endswith(
        "passes the confirmation**."
    )
    assert "fails" in render("evidence", [passed, failed], ["", ""]).splitlines()[-1]
    assert "fails" in render("evidence", [], [])
