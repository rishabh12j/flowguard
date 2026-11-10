import re
from collections import Counter
from datetime import datetime, timedelta

import pytest

from flowguard.benchmark.families_next import NEXT_FAMILIES
from flowguard.benchmark.generate import related
from flowguard.benchmark.generate_next import generate
from flowguard.domain.hypotheses import CATEGORY_DEFINITIONS
from flowguard.domain.remediation import CATALOGUE

FAMILIES = {family.name: family for family in NEXT_FAMILIES}


@pytest.fixture(scope="module")
def built():
    return generate(2031)


def truths(benches):
    return [t for bench in benches.values() for t in bench.truths.values()]


def test_the_families_match_the_plan():
    assert sorted(f.number for f in NEXT_FAMILIES) == list(range(1, 41))
    assert len(FAMILIES) == 40
    assert Counter(f.group for f in NEXT_FAMILIES) == {
        "change": 24,
        "nothing_changed": 8,
        "no_cause": 8,
    }
    for family in NEXT_FAMILIES:
        assert family.category in CATEGORY_DEFINITIONS
        assert (family.category == "unknown") == (family.group == "no_cause")
        assert all(action in CATALOGUE for action, _ in family.plan)
        # A cause has a plan; a change-free cause has no change to roll back.
        assert bool(family.plan) == (family.group != "no_cause")
        if family.group != "change":
            assert not family.changes
            assert all(target != "CHANGE" for _, target in family.plan)


def test_the_same_seed_gives_the_same_benchmark(built):
    again, _ = generate(2031)
    benches, _ = built

    for split in ("dev", "test"):
        assert again[split].incidents == benches[split].incidents
        assert again[split].truths == benches[split].truths
        assert again[split].logs == benches[split].logs


def test_the_split_follows_the_plan(built):
    benches, assigned = built

    for split, variants, groups in (
        ("dev", 5, {"change": 6, "nothing_changed": 2, "no_cause": 2}),
        ("test", 10, {"change": 18, "nothing_changed": 6, "no_cause": 6}),
    ):
        names = [n for n, (_, s) in assigned.items() if s == split]
        assert Counter(FAMILIES[n].group for n in names) == groups
        # Half of each group in each split has a precedent.
        with_precedent = Counter(FAMILIES[n].group for n in names if assigned[n][0])
        assert with_precedent == {group: count // 2 for group, count in groups.items()}
        families = Counter(t["family"] for t in benches[split].truths.values())
        assert families == dict.fromkeys(names, variants)
        assert {t["split"] for t in benches[split].truths.values()} == {split}


def test_ids_are_unique_across_both_folders(built):
    benches, _ = built
    ids = [
        *(i for b in benches.values() for i in b.incidents),
        *(
            d["deployment_id"]
            for b in benches.values()
            for ds in b.deployments.values()
            for d in ds
        ),
        *(
            e["event_id"]
            for b in benches.values()
            for logs in b.logs.values()
            for e in logs
        ),
        *(path for b in benches.values() for path in b.documents),
    ]

    assert len(ids) == len(set(ids))


def test_document_ids_are_numbered_and_precedent_decides_the_documents(built):
    benches, assigned = built
    for bench in benches.values():
        for path in bench.documents:
            assert re.fullmatch(r"\w+/(RB|SPEC|HIST)-\d{5}\.md", path), path
    for truth in truths(benches):
        kinds = {i.split("-")[0] for i in truth["relevant_evidence_ids"]}
        assert "SPEC" in kinds
        has_precedent = assigned[truth["family"]][0]
        assert truth["precedent"] == has_precedent
        assert ({"RB", "HIST"} <= kinds) == has_precedent
        assert not ({"RB", "HIST"} & kinds) or has_precedent


def changes_in_lookback(bench, truth):
    """Deployments and alerts at or upstream of the failing service, in the 24
    hours before the first line."""
    incident = bench.incidents[truth["incident_id"]]
    system = incident["affected_system"]
    family = FAMILIES[truth["family"]]
    upstream = {
        f"{system}-{role}".replace("-store", "-db")
        .replace("-queue", "-events")
        .replace("-partner", "-partner-api")
        .replace("-sftp", "-partner-sftp")
        for role in {family.failing, *related(family.failing, "up")}
    }
    first = next(
        e
        for e in bench.logs[system]
        if e["event_id"] == truth["required_evidence_ids"][0]
    )
    failed_at = datetime.fromisoformat(first["timestamp"])
    found = []
    for record in [*bench.deployments[system], *bench.alerts[system]]:
        at = datetime.fromisoformat(record.get("timestamp") or record["fired_at"])
        if (
            failed_at - timedelta(hours=24) < at < failed_at
            and record["service"] in upstream
        ):
            found.append(record)
    return found


def test_a_cause_with_nothing_changed_has_no_change_in_the_lookback(built):
    benches, _ = built
    for bench in benches.values():
        for truth in bench.truths.values():
            if truth["group"] == "nothing_changed":
                assert changes_in_lookback(bench, truth) == []
                assert len(truth["required_evidence_ids"]) == 1


def test_half_of_each_no_cause_familys_variants_have_a_harmless_change(built):
    benches, _ = built
    for split, expected in (("dev", 3), ("test", 5)):
        bench = benches[split]
        with_change = Counter(
            t["family"]
            for t in bench.truths.values()
            if t["group"] == "no_cause" and changes_in_lookback(bench, t)
        )
        no_cause = {
            t["family"] for t in bench.truths.values() if t["group"] == "no_cause"
        }
        assert with_change == dict.fromkeys(no_cause, expected)


def test_a_cause_with_a_change_requires_it(built):
    benches, _ = built
    for truth in truths(benches):
        required = truth["required_evidence_ids"]
        if truth["group"] != "change":
            continue
        if truth["family"] == "shared_key_new_consumer":
            # The release is downstream, out of the trace's view: its log is required.
            assert required[1].startswith("LOG-")
        else:
            assert required[1].startswith(("DEPLOY-", "ALERT-"))


def test_every_incident_has_noise_from_other_services(built):
    benches, _ = built
    for bench in benches.values():
        for truth in bench.truths.values():
            incident = bench.incidents[truth["incident_id"]]
            start = datetime.fromisoformat(incident["start_time"])
            end = datetime.fromisoformat(incident["end_time"])
            failing = FAMILIES[truth["family"]].failing
            others = [
                e
                for e in bench.logs[incident["affected_system"]]
                if start <= datetime.fromisoformat(e["timestamp"]) <= end
                and not e["service"].endswith(failing)
                and e["level"] == "INFO"
            ]
            assert len(others) >= 2
