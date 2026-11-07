from datetime import datetime, timedelta

import pytest

from flowguard.benchmark.families import FAMILIES
from flowguard.benchmark.generate import EDGES, generate, related
from flowguard.domain.hypotheses import CATEGORY_DEFINITIONS
from flowguard.evaluation.investigations import wilson

SMALL = {"dev_variants": 2, "test_cases": 22}


def small(seed: int = 7):
    return generate(seed, **SMALL)


def test_the_same_seed_gives_the_same_benchmark():
    first, second = small(), small()

    assert first.incidents == second.incidents
    assert first.truths == second.truths
    assert first.logs == second.logs


def test_a_different_seed_gives_a_different_benchmark():
    assert small(7).incidents != small(8).incidents


def test_every_category_has_one_dev_family_and_one_test_family():
    for split in ("dev", "test"):
        categories = sorted(f.category for f in FAMILIES if f.split == split)
        assert categories == sorted(CATEGORY_DEFINITIONS)


def test_the_counts_follow_the_split():
    splits = [truth["split"] for truth in small().truths.values()]

    assert splits.count("dev") == 22
    assert splits.count("test") == 22


def test_incidents_are_far_enough_apart_to_stay_separate():
    starts = sorted(
        datetime.fromisoformat(incident["start_time"])
        for incident in small().incidents.values()
    )

    gaps = [later - earlier for earlier, later in zip(starts, starts[1:], strict=False)]
    assert min(gaps) > timedelta(hours=24 + 3)


def test_required_evidence_exists():
    bench = small()
    known = {
        *(log["event_id"] for logs in bench.logs.values() for log in logs),
        *(d["deployment_id"] for ds in bench.deployments.values() for d in ds),
        *(a["alert_id"] for alerts in bench.alerts.values() for a in alerts),
        *(m["series_id"] for ms in bench.metrics.values() for m in ms),
    }

    for truth in bench.truths.values():
        assert set(truth["required_evidence_ids"]) <= known


def test_abstain_cases_have_no_change_upstream_before_the_errors():
    bench = small()
    for incident_id, truth in bench.truths.items():
        if truth["expected_outcome"] != "abstain":
            continue
        system = bench.incidents[incident_id]["affected_system"]
        family = next(f for f in FAMILIES if f.name == truth["family"])
        upstream = {
            f"{system}-{role}"
            for role in {family.failing, *related(family.failing, "up")}
        }
        first_error = next(
            log
            for log in bench.logs[system]
            if log["event_id"] == truth["required_evidence_ids"][0]
        )
        failed_at = datetime.fromisoformat(first_error["timestamp"])
        for deployment in bench.deployments[system]:
            at = datetime.fromisoformat(deployment["timestamp"])
            nearby = failed_at - timedelta(hours=24) < at < failed_at
            assert not (nearby and deployment["service"] in upstream), deployment


def test_the_topology_has_no_cycles():
    for a, _ in EDGES:
        assert a not in related(a, "up")


@pytest.mark.parametrize(
    "successes, total, interval",
    [(0, 0, (0.0, 0.0)), (5, 5, (0.566, 1.0)), (125, 250, (0.438, 0.562))],
)
def test_wilson_intervals(successes, total, interval):
    assert wilson(successes, total) == interval


def test_a_development_set_gives_every_family_the_same_variants_all_dev():
    bench = generate(7, dev_variants=2, development=True)
    truths = list(bench.truths.values())

    assert len(truths) == 2 * len(FAMILIES)
    assert {truth["split"] for truth in truths} == {"dev"}
    families = [truth["family"] for truth in truths]
    assert all(families.count(family.name) == 2 for family in FAMILIES)
