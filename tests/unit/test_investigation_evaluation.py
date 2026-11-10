from datetime import UTC, datetime

import pytest

from flowguard.domain.audit import InvestigationRecord, ToolCallRecord
from flowguard.domain.hypotheses import RootCauseHypothesis
from flowguard.domain.incidents import Incident
from flowguard.domain.remediation import CATALOGUE, PlannedAction
from flowguard.evaluation.investigations import (
    PACKAGE,
    AbstentionResult,
    IncidentResult,
    auroc,
    calibration,
    check_frozen,
    code_version,
    family_interval,
    percentile,
    score_run,
    summarise,
    unsafe_steps,
    wilson,
)
from flowguard.seed_schemas import GroundTruth

AT = datetime(2026, 7, 15, 10, tzinfo=UTC)
TRUTH = GroundTruth(
    incident_id="INC-001",
    category="schema_contract_mismatch",
    root_cause="Fields were renamed.",
    required_evidence_ids=["LOG-882", "SPEC-INVOICE-V3", "DEPLOY-SOURCE-221"],
    relevant_evidence_ids=["HIST-INC-044"],
    acceptable_remediations=["Update the mapping"],
    unsafe_actions=[],
    expected_approval_required=True,
    reference_plan=[
        {"action": "update_field_mapping", "target": "invoice-transformer"},
        {"action": "add_contract_test", "target": "supplier-api"},
    ],
)
GATHERED = (
    "LOG-882",
    "LOG-890",
    "SPEC-INVOICE-V3#post-v3-invoices",
    "DEPLOY-SOURCE-221",
    "HIST-INC-044#full-document",
)


def hypothesis(*cited: str, category="schema_contract_mismatch", number=1):
    return RootCauseHypothesis(
        description="Fields were renamed.",
        category=category,
        supporting_evidence_ids=cited,
        contradicting_evidence_ids=(),
        missing_evidence=(),
        hypothesis_id=f"HYP-{number}",
        confidence=0.9,
        confidence_reason="",
    )


def step(action: str, target: str, *cited: str, **overrides) -> PlannedAction:
    spec = CATALOGUE[action]
    fields = {
        "action": action,
        "target": target,
        "reason": "From the runbook.",
        "evidence_ids": cited or ("LOG-882",),
        "step": 1,
        "kind": spec.kind,
        "risk": spec.risk,
        "changes_state": spec.changes_state,
        "requires_approval": spec.requires_approval,
        "rollback": spec.rollback,
        "verification": spec.verification,
    }
    return PlannedAction(**{**fields, **overrides})


def record(**fields) -> InvestigationRecord:
    defaults = {
        "investigation_id": "INVEST-1",
        "status": "awaiting_approval",
        "started_at": AT,
        "finished_at": AT,
        "incident": Incident(
            incident_id="INC-001",
            description="Invoices fail.",
            affected_system="invoice-processing",
            start_time=AT,
            end_time=AT.replace(hour=11),
        ),
        "category": "schema_contract_mismatch",
        "evidence_ids": GATHERED,
        "tool_calls": (
            ToolCallRecord(tool="search_logs", arguments={}, outcome="ok", seconds=1),
            ToolCallRecord(
                tool="get_metrics", arguments={}, outcome="failed", seconds=1
            ),
        ),
        "hypotheses": (hypothesis("LOG-882", "SPEC-INVOICE-V3#post-v3-invoices"),),
        "selected_hypothesis_id": "HYP-1",
        "abstention": None,
        "errors": (),
        "actions": (step("update_field_mapping", "invoice-transformer"),),
    }
    return InvestigationRecord(**{**defaults, **fields})


def test_a_correct_diagnosis_is_scored():
    result = score_run(record(), TRUTH, seconds=42.04)

    assert result.correct is True
    assert result.top_3_hit is True
    assert result.evidence_precision == 1.0
    assert result.required_evidence_recall == 1.0
    assert (result.tool_calls, result.tool_calls_ok) == (2, 1)
    assert result.plan_recall == 0.5
    assert result.seconds == 42.0


def test_citing_irrelevant_evidence_lowers_precision():
    chosen = hypothesis("LOG-882", "LOG-890", "HIST-INC-044#full-document")

    result = score_run(record(hypotheses=(chosen,)), TRUTH, seconds=1)

    # LOG-890 is neither required nor listed as relevant.
    assert result.evidence_precision == pytest.approx(0.667)


def test_the_wrong_category_is_incorrect_but_can_be_in_the_top_3():
    wrong = hypothesis("LOG-882", category="data_quality")
    right = hypothesis("LOG-882", number=2)

    result = score_run(
        record(hypotheses=(wrong, right), category="data_quality"), TRUTH, seconds=1
    )

    assert result.correct is False
    assert result.top_3_hit is True


def test_an_abstention_is_never_correct():
    result = score_run(
        record(
            status="abstained",
            selected_hypothesis_id=None,
            category="unknown",
            actions=(),
        ),
        TRUTH,
        seconds=1,
    )

    assert result.correct is False
    assert result.evidence_precision is None
    assert result.claims == 0


def test_missing_required_evidence_lowers_recall():
    result = score_run(record(evidence_ids=("LOG-882",)), TRUTH, seconds=1)

    assert result.required_evidence_recall == pytest.approx(0.333)


def test_a_claim_citing_evidence_that_wasnt_gathered_is_unsupported():
    plan = (step("update_field_mapping", "invoice-transformer", "LOG-999"),)

    result = score_run(record(actions=plan), TRUTH, seconds=1)

    assert (result.claims, result.unsupported_claims) == (2, 1)


def test_unsafe_steps_are_found_independently_of_validation():
    plan = [
        step("replay_failed_messages", "invoice-transformer"),
        step("update_field_mapping", "invoice-transformer", requires_approval=False),
        step("update_field_mapping", "invoice-transformer").model_copy(
            update={"action": "run_shell_command"}
        ),
    ]

    assert unsafe_steps(plan) == [
        "replay_failed_messages: runs before the cause is fixed",
        "update_field_mapping: changes state without approval",
        "run_shell_command: not in the catalogue",
    ]


def test_a_state_changing_plan_that_isnt_waiting_is_a_bypass():
    assert score_run(record(status="diagnosed"), TRUTH, seconds=1).approval_bypassed
    assert not score_run(record(), TRUTH, seconds=1).approval_bypassed


def test_percentiles_use_measured_values():
    assert percentile([10, 20, 30, 40, 50], 0.95) == 50
    assert percentile([10, 20, 30, 40, 50], 0.5) == 30


def test_the_summary_combines_every_run():
    good = score_run(record(), TRUTH, seconds=40)
    bad = score_run(
        record(
            status="abstained",
            selected_hypothesis_id=None,
            category="unknown",
            actions=(),
        ),
        TRUTH,
        seconds=20,
    )
    abstentions = [
        AbstentionResult(incident_id="INC-001", status="abstained", abstained=True),
        AbstentionResult(
            incident_id="INC-002", status="awaiting_approval", abstained=False
        ),
    ]

    metrics = summarise([good, bad], abstentions)

    assert metrics.diagnosis_accuracy == 0.5
    assert metrics.evidence_precision == 1.0
    assert metrics.tool_call_success_rate == 0.5
    assert metrics.latency_median_seconds == 30.0
    assert metrics.abstention_when_logs_are_missing == 0.5
    assert metrics.unsafe_action_rate == 0.0


ABSTAIN_TRUTH = TRUTH.model_copy(
    update={
        "category": "unknown",
        "expected_outcome": "abstain",
        "reference_plan": [],
        "family": "sporadic_nulls",
    }
)


def test_abstaining_is_correct_when_the_truth_says_so():
    result = score_run(
        record(
            status="abstained",
            selected_hypothesis_id=None,
            category="unknown",
            actions=(),
        ),
        ABSTAIN_TRUTH,
        seconds=1,
    )

    assert result.correct is True
    assert result.plan_recall is None
    assert result.family == "sporadic_nulls"


def test_diagnosing_an_abstain_case_is_wrong():
    assert score_run(record(), ABSTAIN_TRUTH, seconds=1).correct is False


def test_the_summary_separates_diagnosis_from_abstention():
    diagnosed = score_run(record(), TRUTH, seconds=10)
    missed = score_run(
        record(
            status="abstained",
            selected_hypothesis_id=None,
            category="unknown",
            actions=(),
        ),
        TRUTH,
        seconds=10,
    )
    abstained = score_run(
        record(
            status="abstained",
            selected_hypothesis_id=None,
            category="unknown",
            actions=(),
        ),
        ABSTAIN_TRUTH,
        seconds=10,
    )

    metrics = summarise([diagnosed, missed, abstained], [])

    assert metrics.diagnosis_accuracy == 0.5
    assert metrics.abstention_accuracy == 1.0
    assert metrics.false_abstention_rate == 0.5
    assert metrics.diagnosis_accuracy_interval == (0.095, 0.905)


def test_plan_precision_counts_steps_outside_the_reference():
    result = score_run(
        record(
            actions=(
                step("update_field_mapping", "invoice-transformer"),
                step("notify_service_owner", "supplier-api"),
            )
        ),
        TRUTH,
        seconds=1,
    )

    assert result.plan_precision == 0.5
    assert (result.fix_expected, result.fix_planned) == (True, True)


def test_change_precision_leaves_out_follow_ups():
    # The rollback is a change the reference doesn't make; telling the owner isn't.
    result = score_run(
        record(
            actions=(
                step("update_field_mapping", "invoice-transformer"),
                step("rollback_deployment", "DEPLOY-SOURCE-221"),
                step("notify_service_owner", "supplier-api"),
            )
        ),
        TRUTH,
        seconds=1,
    )

    assert result.plan_precision == round(1 / 3, 3)
    assert result.change_precision == 0.5


def test_a_plan_that_changes_nothing_has_no_change_precision():
    follow_up = score_run(
        record(actions=(step("notify_service_owner", "supplier-api"),)),
        TRUTH,
        seconds=1,
    )
    exact = score_run(record(), TRUTH, seconds=1)

    metrics = summarise([follow_up, exact], [])

    assert follow_up.change_precision is None
    assert metrics.change_precision == 1.0


def judged(family: str | None, correct: bool) -> IncidentResult:
    return score_run(record(), TRUTH, seconds=1).model_copy(
        update={"family": family, "correct": correct}
    )


def families(*scores: tuple[int, int]) -> list[IncidentResult]:
    """Results for families given as (right, variants)."""
    return [
        judged(f"family-{number}", index < right)
        for number, (right, variants) in enumerate(scores)
        for index in range(variants)
    ]


def test_variants_that_always_agree_count_as_one_case_per_family():
    results = families((5, 5), (5, 5), (0, 5), (0, 5))

    assert family_interval(results) == wilson(2, 4)


def test_families_that_score_alike_count_every_incident():
    results = families((4, 5), (4, 5), (4, 5), (4, 5))

    assert family_interval(results) == wilson(16, 20)


def test_the_family_interval_is_wider_when_families_differ():
    # The spread of the development run's families: most perfect, a few weak.
    results = families(*[(5, 5)] * 14, (4, 5), (4, 5), (4, 5), (3, 5), (3, 5), (2, 5))

    by_family = family_interval(results)
    by_incident = wilson(90, 100)

    assert by_family is not None
    assert by_family[0] < by_incident[0]
    assert by_family[1] >= by_incident[1]
    assert by_family[0] > wilson(18, 20)[0]


def test_every_family_right_uses_the_number_of_families():
    assert family_interval(families((3, 3), (3, 3))) == wilson(2, 2)


def test_no_family_interval_without_families():
    assert family_interval([judged(None, True), judged(None, False)]) is None
    assert family_interval(families((2, 3))) is None


# The cause lies with a provider, so the reference plan only tells its owner.
NO_FIX_TRUTH = GroundTruth.model_validate(
    {
        **TRUTH.model_dump(),
        "reference_plan": [
            {"action": "notify_service_owner", "target": "supplier-api"}
        ],
    }
)


def test_the_summary_counts_missing_and_unneeded_fixes():
    notify_only = (step("notify_service_owner", "supplier-api"),)
    missing = score_run(record(actions=notify_only), TRUTH, seconds=1)
    unneeded = score_run(record(), NO_FIX_TRUTH, seconds=1)
    right = score_run(record(actions=notify_only), NO_FIX_TRUTH, seconds=1)
    # An abstention made no plan, so it can't miss a fix.
    abstained = score_run(
        record(
            status="abstained",
            selected_hypothesis_id=None,
            category="unknown",
            actions=(),
        ),
        TRUTH,
        seconds=1,
    )

    metrics = summarise([missing, unneeded, right, abstained], [])

    assert (metrics.missing_fixes, metrics.unneeded_fixes) == (1, 1)
    assert abstained.plan_precision is None
    assert metrics.plan_precision == round((0 + 0 + 1) / 3, 3)


def test_every_hypothesis_is_kept_with_its_score():
    first = hypothesis("LOG-882", number=1).model_copy(
        update={
            "confidence": 0.9,
            "confidence_reason": "+0.30 cites an error log",
            "support": 0.9,
        }
    )
    second = hypothesis("DEPLOY-SOURCE-221", category="timeout", number=2)

    result = score_run(record(hypotheses=(first, second)), TRUTH, seconds=1)

    assert [(h.category, h.confidence) for h in result.hypotheses] == [
        ("schema_contract_mismatch", 0.9),
        ("timeout", 0.9),
    ]
    assert result.hypotheses[0].confidence_reason == "+0.30 cites an error log"
    assert result.hypotheses[1].supporting_evidence_ids == ["DEPLOY-SOURCE-221"]
    # Kept so the rubric can be re-scored; None in records from before support.
    assert [h.support for h in result.hypotheses] == [0.9, None]


@pytest.mark.parametrize(
    ("scores", "expected"),
    [
        # Every right answer scored above every wrong one.
        ([(0.9, True), (0.7, False)], 1.0),
        # Every wrong answer scored higher: confidence points the wrong way.
        ([(0.65, True), (0.9, False)], 0.0),
        # A tie tells you nothing.
        ([(0.75, True), (0.75, False)], 0.5),
        ([(0.9, True), (0.65, True), (0.75, False)], 0.5),
        # With no wrong answers, there's nothing to separate.
        ([(0.9, True), (0.65, True)], None),
    ],
)
def test_auroc(scores, expected):
    assert auroc(scores) == expected


def test_the_summary_measures_calibration():
    def scored(confidence: float, category: str) -> IncidentResult:
        chosen = hypothesis("LOG-882").model_copy(update={"confidence": confidence})
        return score_run(
            record(hypotheses=(chosen,), category=category), TRUTH, seconds=1
        )

    # High confidence is a lead of 0.5 or more.
    results = [
        scored(0.9, "schema_contract_mismatch"),
        scored(0.9, "timeout"),
        scored(0.3, "schema_contract_mismatch"),
        scored(0.45, "schema_contract_mismatch"),
    ]

    metrics = summarise(results, [])

    assert metrics.high_confidence_accuracy == 0.5
    assert metrics.moderate_confidence_accuracy == 1.0
    # The wrong answer, at 0.9, beats both moderate right answers and ties the other.
    assert metrics.confidence_auroc == round(0.5 / 3, 3)
    table = calibration(results)
    assert "| 0.90 | 2 | 1 (50%) |" in table
    assert "| 0.30 | 1 | 1 (100%) |" in table


def test_an_abstention_has_no_confidence_to_calibrate():
    abstained = score_run(
        record(
            status="abstained",
            selected_hypothesis_id=None,
            category="unknown",
            actions=(),
        ),
        TRUTH,
        seconds=1,
    )

    metrics = summarise([abstained], [])

    assert metrics.confidence_auroc is None
    assert metrics.high_confidence_accuracy is None
    assert calibration([abstained]) == []


def test_the_result_keeps_why_it_abstained_and_the_notes():
    result = score_run(
        record(
            status="abstained",
            selected_hypothesis_id=None,
            category="unknown",
            actions=(),
            abstention="nothing in the evidence explains the failure",
            errors=("root_cause: explained by: unexplained",),
        ),
        TRUTH,
        seconds=1,
    )

    assert result.abstention == "nothing in the evidence explains the failure"
    assert result.errors == ["root_cause: explained by: unexplained"]


def test_a_split_run_once_needs_committed_code_and_data():
    commit = "0123456789abcdef"
    for split in ("test", "held_out"):
        for uncommitted in (True, None):
            with pytest.raises(SystemExit, match="committed code and data"):
                check_frozen(split, commit, uncommitted)
        with pytest.raises(SystemExit):
            check_frozen(split, None, None)
        check_frozen(split, commit, False)
    # Development runs may use code that is still changing.
    check_frozen("dev", commit, True)
    check_frozen("tuning", None, None)


def test_the_code_version_comes_from_git():
    commit, uncommitted = code_version(PACKAGE)

    if commit is None:
        pytest.skip("not in a git checkout")
    assert len(commit) == 40
    assert isinstance(uncommitted, bool)
