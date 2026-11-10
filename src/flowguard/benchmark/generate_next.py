"""Generates the benchmark planned in docs/next-benchmark.md, from its 40 families.

    python -m flowguard.benchmark.generate_next --seed 2031 --out data/benchmark-2031

The seed first decides which families have a precedent (half of each group) and
which are for development (6 with a change, 2 with nothing changed, 2 with no
cause) or the test set (the other 18, 6 and 6). Development families get 5
variants each and test families 10, written to separate folders, dev/ and test/,
so a development run never sees a test family's documents. The same seed always
gives the same benchmark.

What differs from the first generator: document IDs are numbered, never the
family's code; families without a precedent have no runbook or past incident;
causes with nothing changed before them have no change in the lookback; half of
each no-cause family's variants get a harmless change upstream inside the
lookback; and every incident has a few unrelated log lines from other services.
"""

import argparse
import random
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from flowguard.benchmark.families import Role
from flowguard.benchmark.families_next import NEXT_FAMILIES, Group, NextFamily
from flowguard.benchmark.generate import (
    DOMAINS,
    HARMLESS_CHANGES,
    NODE_TYPES,
    SPACING,
    START,
    Benchmark,
    SystemInfo,
    add_map,
    alert,
    deployment,
    document_text,
    iso,
    log,
    metric,
    related,
    system,
    write,
)
from flowguard.domain.remediation import CATALOGUE

DEV_VARIANTS = 5
TEST_VARIANTS = 10
# How many families of each group are for development; the rest are for the test.
DEV_FAMILIES: dict[Group, int] = {"change": 6, "nothing_changed": 2, "no_cause": 2}
STATUSES = ("ON_HOLD", "PARTIAL", "DISPUTED")
COUNTRIES = ("DE", "FR", "IN", "BR", "JP")
NOISE = (
    "Health check passed",
    "Cache refreshed",
    "Scheduled cleanup finished",
    "Connection pool at 40 percent",
    "Heartbeat sent",
    "Processed a batch normally",
)


def assign(rng: random.Random) -> dict[str, tuple[bool, str]]:
    """Each family's precedent and split: (has a precedent, dev or test)."""
    assigned = {}
    for group, dev_count in DEV_FAMILIES.items():
        members = [f.name for f in NEXT_FAMILIES if f.group == group]
        rng.shuffle(members)
        half = len(members) // 2
        for precedent, subgroup in ((True, members[:half]), (False, members[half:])):
            chosen = list(subgroup)
            rng.shuffle(chosen)
            for index, name in enumerate(chosen):
                split = "dev" if index < dev_count // 2 else "test"
                assigned[name] = (precedent, split)
    return assigned


def add_documents(
    bench: Benchmark,
    info: SystemInfo,
    family: NextFamily,
    precedent: bool,
    fill: Any,
    known: dict[tuple[str, str], str],
) -> list[str]:
    """The family's documents in this system, added once: always its API spec, and
    a runbook and a past incident when it has a precedent. Known maps (family,
    kind) to the IDs already written for this system."""
    kinds = ["api_spec"] + (["runbook", "historical_incident"] if precedent else [])
    folders = {
        "runbook": ("runbooks", "RB", family.runbook),
        "api_spec": ("api_specs", "SPEC", family.spec),
        "historical_incident": ("historical_incidents", "HIST", family.history),
    }
    ids = []
    for kind in kinds:
        if (family.name, kind) in known:
            ids.append(known[family.name, kind])
            continue
        folder, prefix, document = folders[kind]
        document_id = bench.next_id(prefix)
        known[family.name, kind] = document_id
        header = {
            "document_id": document_id,
            "document_type": kind,
            "title": fill(document.title),
            "system": info.domain,
            "service": info.names[family.failing],
            "version": "1.0",
            "effective_date": "2026-06-01",
            "is_current": "true",
        }
        front = "".join(f"{field}: {value}\n" for field, value in header.items())
        bench.documents[f"{folder}/{document_id}.md"] = (
            f"---\n{front}---\n\n{document_text(document, kind, fill)}"
        )
        ids.append(document_id)
    return ids


def add_incident(
    bench: Benchmark, rng: random.Random, number: int, family: NextFamily,
    precedent: bool, split: str, decoy: bool, info: SystemInfo, day: datetime,
    known: dict[tuple[str, str], str],
) -> None:  # fmt: skip
    names = info.names
    variables = {
        **info.variables,
        "n": rng.randint(10000, 99999),
        "code": f"PX-{rng.randint(1000, 9999)}",
        "skew": rng.choice((5, 7, 9)),
        "status": rng.choice(STATUSES),
        "country": rng.choice(COUNTRIES),
        "mb": rng.randint(9, 30),
        "quota": rng.choice((5000, 10000, 20000)),
    }
    failure = day.replace(
        hour=rng.randint(3, 20), minute=rng.randint(0, 59), second=rng.randint(0, 59)
    )

    def fill(text: str) -> str:
        return text.format(
            **names,
            **variables,
            domain=info.domain,
            Domain=info.domain.capitalize(),
            time=f"{failure:%H:%M} UTC",
        )

    domain = info.domain
    failing = names[family.failing]
    map_id = add_map(bench, info)
    documents = add_documents(bench, info, family, precedent, fill, known)

    # The changes that explain the failure.
    change_ids: list[str] = []
    causal_deployment: str | None = None
    for change in family.changes:
        service = names[change.role]
        if change.kind == "deployment":
            at = failure - timedelta(minutes=rng.randint(30, 20 * 60))
            change_id = deployment(
                bench, domain, at, service, [fill(t) for t in change.text]
            )
            causal_deployment = causal_deployment or change_id
        elif change.kind == "alert":
            at = failure - timedelta(minutes=rng.randint(5, 20 * 60))
            change_id = alert(
                bench, domain, at, service, fill(change.text[0]), fill(change.text[1])
            )
        else:
            change_id = metric(
                bench, domain, rng, failure, service, change, variables["limit"]
            )
        change_ids.append(change_id)

    # Decoys: changes that didn't cause the failure. These three are outside the
    # lookback or downstream, so the investigation leaves them out.
    upstream = sorted(related(family.failing, "up"))
    downstream = sorted(related(family.failing, "down"))
    causal_roles = {change.role for change in family.changes}
    if rng.random() < 0.7:
        role = rng.choice(sorted(NODE_TYPES))
        at = failure - timedelta(hours=rng.uniform(26, 34))
        deployment(bench, domain, at, names[role], [rng.choice(HARMLESS_CHANGES)])
    if downstream and rng.random() < 0.5:
        at = failure - timedelta(minutes=rng.randint(30, 20 * 60))
        role = rng.choice(downstream)
        deployment(bench, domain, at, names[role], [rng.choice(HARMLESS_CHANGES)])
    if downstream and rng.random() < 0.3:
        at = failure - timedelta(minutes=rng.randint(30, 20 * 60))
        alert(
            bench,
            domain,
            at,
            names[rng.choice(downstream)],
            "Disk usage above 80 percent",
            "Cleanup is scheduled.",
        )
    # A harmless change upstream inside the lookback: for a cause with a change,
    # in 30% of variants; for no cause, in the variants chosen for it, so a change
    # alone no longer separates the two. Never for a cause with nothing changed.
    # An hour or more before the first line, so it falls in the lookback even when
    # no error anchors it and the search starts from the incident's window.
    if family.group == "change":
        candidates = [role for role in upstream if role not in causal_roles]
        if candidates and rng.random() < 0.3:
            at = failure - timedelta(minutes=rng.randint(60, 20 * 60))
            role = rng.choice(candidates)
            deployment(bench, domain, at, names[role], [rng.choice(HARMLESS_CHANGES)])
    elif family.group == "no_cause" and decoy:
        at = failure - timedelta(minutes=rng.randint(60, 20 * 60))
        role = rng.choice(sorted({family.failing, *upstream}))
        deployment(bench, domain, at, names[role], [rng.choice(HARMLESS_CHANGES)])

    # The main lines: a burst of errors, errors scattered over hours that succeed
    # when retried, or a single event and the sign that things were normal again.
    main_ids: list[str] = []
    recovery_ids: list[str] = []
    message = fill(family.error)
    last = failure
    if family.pattern == "burst":
        at = failure
        for _ in range(rng.randint(2, 4)):
            main_ids.append(
                log(bench, domain, at, failing, family.level, message, family.exception)
            )
            last = at
            at += timedelta(seconds=rng.randint(*family.gap))
    elif family.pattern == "scattered":
        offsets = [0] + sorted(rng.sample(range(20, 300), rng.randint(2, 4)))
        for offset in offsets:
            at = failure + timedelta(minutes=offset)
            main_ids.append(
                log(bench, domain, at, failing, family.level, message, family.exception)
            )
            if family.recovery:
                retried = at + timedelta(seconds=rng.randint(5, 50))
                recovery_ids.append(
                    log(bench, domain, retried, failing, "INFO", fill(family.recovery))
                )
                last = retried
    else:
        main_ids.append(
            log(
                bench, domain, failure, failing, family.level, message, family.exception
            )
        )
        if family.recovery:
            later = failure + timedelta(minutes=family.recovery_after)
            recovery_ids.append(
                log(bench, domain, later, failing, "INFO", fill(family.recovery))
            )
            last = later

    extra_ids = []
    for role, level, text, offset in family.extra_logs:
        at = failure + timedelta(minutes=offset)
        extra_ids.append(log(bench, domain, at, names[role], level, fill(text)))
        last = max(last, at)

    earliest = min([0, *(offset for _, _, _, offset in family.extra_logs)])
    start = failure - timedelta(minutes=rng.randint(10, 40))
    start = min(start, failure + timedelta(minutes=earliest - 5)).replace(second=0)
    end = max(start + timedelta(hours=2), failure + timedelta(hours=1))
    end = max(end, last + timedelta(minutes=30))
    log(
        bench,
        domain,
        start + timedelta(minutes=2),
        failing,
        "INFO",
        "Processed a batch normally",
    )

    # Noise: a few ordinary lines from other services.
    others: list[Role] = [role for role in NODE_TYPES if role != family.failing]
    span = int((end - start).total_seconds())
    for _ in range(rng.randint(2, 4)):
        at = start + timedelta(seconds=rng.randint(0, span))
        log(bench, domain, at, names[rng.choice(others)], "INFO", rng.choice(NOISE))

    incident_id = f"BENCH-{number:04d}"
    bench.incidents[incident_id] = {
        "incident_id": incident_id,
        "description": fill(rng.choice(family.descriptions)),
        "affected_system": domain,
        "start_time": iso(start),
        "end_time": iso(end),
    }
    plan = []
    for action, target in family.plan:
        resolved = causal_deployment if target == "CHANGE" else names[target]
        if resolved is None:
            raise ValueError(f"{family.name} rolls back a deployment it doesn't have")
        plan.append({"action": action, "target": resolved})
    if family.required_log is not None:
        cause = [extra_ids[family.required_log]]
        supporting = [i for n, i in enumerate(extra_ids) if n != family.required_log]
    else:
        cause = change_ids[:1]
        supporting = [*extra_ids, *change_ids[1:]]
    diagnose = family.group != "no_cause"
    bench.truths[incident_id] = {
        "incident_id": incident_id,
        "split": split,
        "family": family.name,
        "group": family.group,
        "precedent": precedent,
        "expected_outcome": "diagnose" if diagnose else "abstain",
        "category": family.category,
        "root_cause": fill(family.root_cause),
        "required_evidence_ids": [main_ids[0], *cause],
        "relevant_evidence_ids": [
            *main_ids[1:],
            *recovery_ids,
            *supporting,
            *documents,
            map_id,
        ],
        "acceptable_remediations": [fill(text) for text in family.acceptable],
        "unsafe_actions": [fill(text) for text in family.unsafe],
        "expected_approval_required": diagnose
        and any(CATALOGUE[action].changes_state for action, _ in family.plan),
        "reference_plan": plan,
    }


def generate(seed: int) -> tuple[dict[str, Benchmark], dict[str, tuple[bool, str]]]:
    """The development and test benchmarks, and each family's assignment."""
    rng = random.Random(seed)
    assigned = assign(rng)
    systems = {domain: system(domain, rng) for domain in DOMAINS}
    order: list[tuple[NextFamily, int]] = []
    for family in NEXT_FAMILIES:
        _, split = assigned[family.name]
        variants = DEV_VARIANTS if split == "dev" else TEST_VARIANTS
        order += [(family, variant) for variant in range(variants)]
    rng.shuffle(order)
    benches = {"dev": Benchmark(), "test": Benchmark()}
    # Each split keeps its own documents per system.
    documents: dict[tuple[str, str], dict[tuple[str, str], str]] = {}
    for index, (family, variant) in enumerate(order, start=1):
        precedent, split = assigned[family.name]
        bench = benches[split]
        # One counter across both, so no ID appears in both folders.
        bench.counter = max(b.counter for b in benches.values())
        domain = rng.choice(DOMAINS)
        add_incident(
            bench,
            rng,
            index,
            family,
            precedent,
            split,
            # Half of each no-cause family's variants get a harmless change.
            variant % 2 == 0,
            systems[domain],
            START + SPACING * (index - 1),
            documents.setdefault((split, domain), {}),
        )
    return benches, assigned


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the next benchmark.")
    parser.add_argument("--out", type=Path, default=Path("data/benchmark-2031"))
    parser.add_argument("--seed", type=int, default=2031)
    arguments = parser.parse_args()
    benches, assigned = generate(arguments.seed)
    command = (
        "python -m flowguard.benchmark.generate_next "
        f"--seed {arguments.seed} --out {arguments.out.as_posix()}"
    )
    for split, bench in benches.items():
        folder = arguments.out / split
        write(bench, folder, arguments.seed)
        families = sorted({t["family"] for t in bench.truths.values()})
        (folder / "README.md").write_text(
            f"# FlowGuard benchmark from seed {arguments.seed}: {split}\n\n"
            f"Generated by `{command}`. Don't edit by hand: change the families or "
            "the generator, and regenerate.\n\n"
            + (
                "The test set is run once, after FlowGuard is frozen, and never "
                "tuned on.\n\n"
                if split == "test"
                else "For developing FlowGuard. Never report its numbers as accuracy.\n\n"
            )
            + f"{len(bench.incidents)} incidents from {len(families)} families.\n",
            encoding="utf-8",
        )
        groups = Counter((t["group"], t["precedent"]) for t in bench.truths.values())
        print(f"{split}: {len(bench.incidents)} incidents, {len(families)} families")
        for (group, precedent), count in sorted(groups.items()):
            print(f"  {group}, precedent {precedent}: {count}")
    dev = sorted(name for name, (_, split) in assigned.items() if split == "dev")
    print("development families:", ", ".join(dev))


if __name__ == "__main__":
    main()
