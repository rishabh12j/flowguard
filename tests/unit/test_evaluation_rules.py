from test_investigation_evaluation import TRUTH, hypothesis, record

from flowguard.evaluation.investigations import IncidentResult, score_run
from flowguard.evaluation.rules import compare, outcome, render, score_rule


def scored(category, support, rank, signals=(), verdict=None, number=1):
    return hypothesis("LOG-882", category=category, number=number).model_copy(
        update={
            "support": support,
            "proposed_rank": rank,
            "signals": signals,
            "verdict": verdict,
        }
    )


def result(*hypotheses, evidence_score=0.9, expected="schema_contract_mismatch"):
    run = score_run(
        record(hypotheses=hypotheses, evidence_score=evidence_score), TRUTH, seconds=1
    )
    if expected == "unknown":
        return run.model_copy(
            update={"expected_category": "unknown", "expected_outcome": "abstain"}
        )
    return run


# The model's first choice is right but lists a contradiction; a release story,
# second, cites more and outscores it under the rubric.
RIGHT = scored("schema_contract_mismatch", 0.55, 1, ("error_log",), "mechanism")
RELEASE = scored(
    "deployment_or_configuration",
    0.85,
    2,
    ("timeline", "deployment"),
    "trigger_only",
    2,
)


def test_the_new_records_are_kept_on_the_result():
    run = result(RIGHT, RELEASE)

    assert run.evidence_score == 0.9
    assert [h.proposed_rank for h in run.hypotheses] == [1, 2]
    assert run.hypotheses[1].signals == ["timeline", "deployment"]
    assert run.hypotheses[0].verdict == "mechanism"


def test_each_rule_is_applied_to_the_same_run():
    run = result(RIGHT, RELEASE)

    assert outcome(run, "rubric")[0] == "deployment_or_configuration"
    assert outcome(run, "model")[0] == "schema_contract_mismatch"
    assert outcome(run, "checked")[0] == "schema_contract_mismatch"


def test_a_rule_abstains_when_the_evidence_together_is_weak():
    run = result(RIGHT, evidence_score=0.5)

    assert outcome(run, "model") == ("unknown", None)


def test_scores_count_right_wrong_and_abstentions():
    runs: list[IncidentResult] = [
        result(RIGHT, RELEASE),
        result(scored("timeout", 0.4, 1), evidence_score=0.5, expected="unknown"),
    ]

    rubric = score_rule(runs, "rubric")
    model = score_rule(runs, "model")

    assert (rubric.diagnosed, rubric.wrong, rubric.abstained_rightly) == (0, 1, 1)
    assert (model.diagnosed, model.wrong, model.abstained_rightly) == (1, 0, 1)


def test_the_comparison_renders_one_row_per_rule():
    lines = render("run", compare([result(RIGHT, RELEASE)]))

    assert lines[0] == "### run"
    # The header, then one row for each of the five rules.
    assert sum(line.startswith("| ") for line in lines) == 1 + 5
