from datetime import UTC, datetime, timedelta

import pytest

from flowguard.domain.confidence import score
from flowguard.domain.evidence import EvidenceItem
from flowguard.domain.hypotheses import ProposedHypothesis

FAILED_AT = datetime(2026, 7, 15, 9, 43, tzinfo=UTC)


def item(
    evidence_id: str,
    source_type: str,
    *,
    service: str = "invoice-transformer",
    at: datetime | None = None,
    metadata: dict | None = None,
) -> EvidenceItem:
    return EvidenceItem(
        evidence_id=evidence_id,
        source_type=source_type,
        source_name=service,
        timestamp=at,
        title=evidence_id,
        content="Some content.",
        metadata=metadata or {},
    )


FAILURE = item("LOG-882", "log", at=FAILED_AT, metadata={"level": "ERROR"})
WARNING = item("LOG-883", "log", at=FAILED_AT, metadata={"level": "WARN"})
UPSTREAM = item(
    "DEPLOY-SOURCE-221",
    "deployment",
    service="supplier-api",
    at=FAILED_AT - timedelta(hours=1, minutes=38),
)
DOWNSTREAM = item(
    "DEPLOY-WORKFLOW-118",
    "deployment",
    service="invoice-workflow",
    at=FAILED_AT - timedelta(hours=17),
)
TOO_OLD = item(
    "DEPLOY-SOURCE-200",
    "deployment",
    service="supplier-api",
    at=FAILED_AT - timedelta(days=3),
)
AFTER = item(
    "DEPLOY-SOURCE-222",
    "deployment",
    service="supplier-api",
    at=FAILED_AT + timedelta(minutes=5),
)
SPEC = item("SPEC-INVOICE-V3#post-v3-invoices", "api_spec")
PAST = item("HIST-INC-044#full-document", "historical_incident")
MAP = item(
    "DEPMAP-INVOICE",
    "dependency_map",
    service="invoice-processing",
    metadata={
        "edges": [
            {"from": "supplier-api", "to": "invoice-transformer"},
            {"from": "invoice-transformer", "to": "invoice-workflow"},
        ]
    },
)
EVIDENCE = {
    evidence.evidence_id: evidence
    for evidence in (
        FAILURE,
        WARNING,
        UPSTREAM,
        DOWNSTREAM,
        TOO_OLD,
        AFTER,
        SPEC,
        PAST,
        MAP,
    )
}


def hypothesis(*supporting: str, contradicting: tuple[str, ...] = ()):
    return ProposedHypothesis(
        description="supplier-api now sends camelCase fields.",
        supporting_evidence_ids=supporting,
        contradicting_evidence_ids=contradicting,
        missing_evidence=(),
        category="schema_contract_mismatch",
    )


def confidence(*supporting: str, contradicting=(), failure=FAILURE, missing=0):
    proposed = hypothesis(*supporting, contradicting=contradicting)
    return score(proposed, EVIDENCE, failure, missing)[0]


def test_inc_001_root_cause_scores_high():
    result, reason = score(
        hypothesis("LOG-882", "DEPLOY-SOURCE-221", SPEC.evidence_id),
        EVIDENCE,
        FAILURE,
        0,
    )

    assert result == 0.90
    assert reason == (
        "+0.30 cites an error log; "
        "+0.20 a cited deployment came before the first failure; "
        "+0.15 a cited deployment is upstream of the failure; "
        "+0.15 cites an API specification; "
        "+0.10 cites a deployment"
    )


@pytest.mark.parametrize(
    ("supporting", "expected"),
    [
        (("LOG-882",), 0.30),
        (("LOG-883",), 0.0),
        ((SPEC.evidence_id,), 0.15),
        ((PAST.evidence_id,), 0.10),
        (("DEPLOY-SOURCE-221",), 0.45),
        (("DEPLOY-WORKFLOW-118",), 0.30),
        (("DEPLOY-SOURCE-200",), 0.25),
        (("DEPLOY-SOURCE-222",), 0.25),
    ],
)
def test_each_signal_adds_its_points(supporting, expected):
    assert confidence(*supporting) == expected


def test_every_signal_together_scores_one():
    supporting = ("LOG-882", "DEPLOY-SOURCE-221", SPEC.evidence_id, PAST.evidence_id)

    assert confidence(*supporting) == 1.0


def test_without_a_first_failure_timing_and_path_score_nothing():
    assert confidence("DEPLOY-SOURCE-221", failure=None) == 0.10


def test_without_a_map_the_path_scores_nothing():
    evidence = {
        key: value for key, value in EVIDENCE.items() if key != "DEPMAP-INVOICE"
    }
    proposed = hypothesis("DEPLOY-SOURCE-221")

    assert score(proposed, evidence, FAILURE, 0)[0] == 0.30


def test_each_contradiction_costs_point_two():
    result = confidence("LOG-882", contradicting=("LOG-883",))

    assert result == 0.10


def test_each_missing_source_costs_point_one_five():
    assert confidence("LOG-882", "DEPLOY-SOURCE-221", missing=2) == 0.45


def test_never_goes_below_zero():
    assert confidence("LOG-882", contradicting=("LOG-883", SPEC.evidence_id)) == 0.0


def test_a_hypothesis_with_no_signals_says_so():
    assert (
        score(hypothesis("LOG-883"), EVIDENCE, FAILURE, 0)[1] == "no supporting signals"
    )
