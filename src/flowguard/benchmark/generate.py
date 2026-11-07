"""Generates FlowGuard's benchmark: scenario families varied across systems and time.

    python -m flowguard.benchmark.generate --out data/benchmark --seed 2027

The same seed always gives the same benchmark.
"""

import argparse
import json
import random
import shutil
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from flowguard.benchmark.families import FAMILIES, Change, Document, Family, Role

DOMAINS = (
    "billing", "invoicing", "payroll", "shipping", "inventory",
    "claims", "loyalty", "onboarding", "ledger", "procurement",
    "subscriptions", "returns", "pricing", "catalogue", "bookings",
    "payments", "settlements", "rewards", "accounts", "warranty",
)  # fmt: skip
NODE_TYPES: dict[Role, str] = {
    "gateway": "api",
    "processor": "service",
    "store": "database",
    "queue": "queue",
    "worker": "service",
    "partner": "api",
    "exporter": "job",
    "sftp": "sftp",
    "backfill": "job",
    "reports": "job",
}
# An edge from A to B means B depends on A.
EDGES: tuple[tuple[Role, Role], ...] = (
    ("gateway", "processor"),
    ("store", "processor"),
    ("processor", "queue"),
    ("backfill", "queue"),
    ("queue", "worker"),
    ("partner", "worker"),
    ("worker", "exporter"),
    ("exporter", "sftp"),
    ("worker", "reports"),
)
DEV_VARIANTS = 5
TEST_CASES = 250
# Incidents three days apart: no incident's 24-hour lookback can reach another's.
SPACING = timedelta(days=3)
START = datetime(2027, 1, 4, tzinfo=UTC)
FIELDS = ("customer_id", "order_id", "account_id", "supplier_id", "item_id")
SETTINGS = ("PARTNER_API_URL", "QUEUE_URL", "RELAY_HOST", "SERVICE_REGION")
HARMLESS_CHANGES = (
    "Updated the log format",
    "Added a health dashboard",
    "Upgraded the HTTP library to a patch release",
    "Renamed an internal metric",
)


def camel(name: str) -> str:
    first, *rest = name.split("_")
    return first + "".join(part.capitalize() for part in rest)


def related(role: Role, direction: str) -> set[Role]:
    """The roles upstream (what it depends on) or downstream of a role."""
    found: set[Role] = set()
    frontier = {role}
    while frontier:
        if direction == "up":
            frontier = {a for a, b in EDGES if b in frontier} - found
        else:
            frontier = {b for a, b in EDGES if a in frontier} - found
        found |= frontier
    return found


@dataclass
class SystemInfo:
    domain: str
    names: dict[str, str]
    variables: dict[str, Any]
    documents: set[str] = field(default_factory=set)


@dataclass
class Benchmark:
    logs: dict[str, list[dict[str, Any]]] = field(
        default_factory=lambda: defaultdict(list)
    )
    deployments: dict[str, list[dict[str, Any]]] = field(
        default_factory=lambda: defaultdict(list)
    )
    alerts: dict[str, list[dict[str, Any]]] = field(
        default_factory=lambda: defaultdict(list)
    )
    metrics: dict[str, list[dict[str, Any]]] = field(
        default_factory=lambda: defaultdict(list)
    )
    maps: dict[str, dict[str, Any]] = field(default_factory=dict)
    documents: dict[str, str] = field(default_factory=dict)
    incidents: dict[str, dict[str, Any]] = field(default_factory=dict)
    truths: dict[str, dict[str, Any]] = field(default_factory=dict)
    counter: int = 0

    def next_id(self, prefix: str) -> str:
        self.counter += 1
        return f"{prefix}-{self.counter:05d}"


def iso(moment: datetime) -> str:
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def system(domain: str, rng: random.Random) -> SystemInfo:
    names = {
        "gateway": f"{domain}-gateway",
        "processor": f"{domain}-processor",
        "store": f"{domain}-db",
        "queue": f"{domain}-events",
        "worker": f"{domain}-worker",
        "partner": f"{domain}-partner-api",
        "exporter": f"{domain}-exporter",
        "sftp": f"{domain}-partner-sftp",
        "backfill": f"{domain}-backfill",
        "reports": f"{domain}-reports",
    }
    chosen = rng.choice(FIELDS)
    # Per system, so the system's documents agree with every incident in it.
    variables = {
        "field": chosen,
        "camel": camel(chosen),
        "var": rng.choice(SETTINGS),
        "limit": rng.choice((60, 100, 120)),
    }
    return SystemInfo(domain, names, variables)


def document_text(document: Document, kind: str, fill: Any) -> str:
    body = [f"# {fill(document.title)}", ""]
    if kind == "api_spec":
        body += [f"The {fill(document.title)} contract.", ""]
    for heading, text in document.sections:
        body += [f"## {heading}", "", fill(text), ""]
    return "\n".join(body).strip() + "\n"


def add_documents(
    bench: Benchmark, info: SystemInfo, family: Family, fill: Any
) -> dict[str, str]:
    code = f"{info.domain.upper()}-{family.code}"
    ids = {
        "runbook": f"RB-{code}",
        "api_spec": f"SPEC-{code}",
        "historical_incident": f"HIST-{code}",
    }
    folders = {
        "runbook": "runbooks",
        "api_spec": "api_specs",
        "historical_incident": "historical_incidents",
    }
    sources = {
        "runbook": (family.runbook, family.failing),
        "api_spec": (family.spec, family.failing),
        "historical_incident": (family.history, family.failing),
    }
    for kind, document_id in ids.items():
        if document_id in info.documents:
            continue
        info.documents.add(document_id)
        document, role = sources[kind]
        header = {
            "document_id": document_id,
            "document_type": kind,
            "title": fill(document.title),
            "system": info.domain,
            "service": info.names[role],
            "version": "1.0",
            "effective_date": "2026-06-01",
            "is_current": "true",
        }
        front = "".join(f"{key}: {value}\n" for key, value in header.items())
        bench.documents[f"{folders[kind]}/{document_id}.md"] = (
            f"---\n{front}---\n\n{document_text(document, kind, fill)}"
        )
    return ids


def add_map(bench: Benchmark, info: SystemInfo) -> str:
    map_id = f"DEPMAP-{info.domain.upper()}"
    if info.domain not in bench.maps:
        bench.maps[info.domain] = {
            "map_id": map_id,
            "system": info.domain,
            "nodes": [
                {"name": info.names[role], "type": kind}
                for role, kind in NODE_TYPES.items()
            ],
            "edges": [{"from": info.names[a], "to": info.names[b]} for a, b in EDGES],
        }
    return map_id


def log(
    bench: Benchmark, domain: str, at: datetime, service: str, level: str,
    message: str, exception: str | None = None, **metadata: Any,
) -> str:  # fmt: skip
    event_id = bench.next_id("LOG")
    bench.logs[domain].append(
        {
            "event_id": event_id,
            "timestamp": iso(at),
            "service": service,
            "environment": "demo",
            "level": level,
            "correlation_id": f"CORR-{event_id}",
            "message": message,
            "exception_type": exception,
            "metadata": metadata,
        }
    )
    return event_id


def deployment(
    bench: Benchmark, domain: str, at: datetime, service: str, changes: list[str]
) -> str:
    deployment_id = bench.next_id(f"DEPLOY-{domain.upper()}")
    bench.deployments[domain].append(
        {
            "deployment_id": deployment_id,
            "service": service,
            "version": f"{at.month}.{at.day}.{at.hour}",
            "timestamp": iso(at),
            "changes": changes,
            "status": "successful",
        }
    )
    return deployment_id


def alert(
    bench: Benchmark, domain: str, at: datetime, service: str, title: str, text: str
) -> str:
    alert_id = bench.next_id("ALERT")
    bench.alerts[domain].append(
        {
            "alert_id": alert_id,
            "service": service,
            "fired_at": iso(at),
            "severity": "warning",
            "status": "firing",
            "title": title,
            "description": text,
        }
    )
    return alert_id


def metric(
    bench: Benchmark, domain: str, rng: random.Random, failure: datetime,
    service: str, change: Change, limit: int,
) -> str:  # fmt: skip
    threshold = change.threshold or limit
    baseline = change.baseline or round(limit * 0.6)
    peak = change.peak or limit * 6
    # Ten-minute points from three hours before the failure to one hour after. The
    # metric crosses its threshold at the last point before the failure.
    first = (failure - timedelta(hours=3)).replace(second=0)
    first -= timedelta(minutes=first.minute % 10)
    crossing = failure - timedelta(minutes=1)
    crossing = crossing.replace(second=0) - timedelta(minutes=crossing.minute % 10)
    points = []
    moment = first
    while moment <= failure + timedelta(hours=1):
        if moment < crossing:
            value = round(baseline * rng.uniform(0.8, 1.2))
        elif moment == crossing:
            value = round(threshold * 1.4)
        else:
            value = round(peak * rng.uniform(0.85, 1.0))
        points.append({"timestamp": iso(moment), "value": value})
        moment += timedelta(minutes=10)
    series_id = bench.next_id("METRIC")
    bench.metrics[domain].append(
        {
            "series_id": series_id,
            "service": service,
            "metric": change.text[0],
            "unit": change.text[1],
            "threshold": threshold,
            "points": points,
        }
    )
    return series_id


def add_incident(
    bench: Benchmark, rng: random.Random, number: int, family: Family,
    info: SystemInfo, day: datetime,
) -> None:  # fmt: skip
    names = info.names
    variables = {
        **info.variables,
        "n": rng.randint(10000, 99999),
        "code": f"PX-{rng.randint(1000, 9999)}",
    }
    failure = day.replace(
        hour=rng.randint(3, 20), minute=rng.randint(0, 59), second=rng.randint(0, 59)
    )

    def fill(text: str) -> str:
        return text.format(
            **names,
            **variables,
            Domain=info.domain.capitalize(),
            time=f"{failure:%H:%M} UTC",
        )

    domain = info.domain
    failing = names[family.failing]
    map_id = add_map(bench, info)
    documents = add_documents(bench, info, family, fill)

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

    # Decoys: changes that didn't cause the failure.
    upstream = sorted(related(family.failing, "up"))
    downstream = sorted(related(family.failing, "down"))
    causal_roles = {change.role for change in family.changes}
    if rng.random() < 0.7:
        role = rng.choice(sorted(NODE_TYPES))
        at = failure - timedelta(hours=rng.uniform(26, 34))
        deployment(bench, domain, at, names[role], [rng.choice(HARMLESS_CHANGES)])
    if downstream and rng.random() < 0.5:
        at = failure - timedelta(minutes=rng.randint(30, 20 * 60))
        deployment(
            bench,
            domain,
            at,
            names[rng.choice(downstream)],
            [rng.choice(HARMLESS_CHANGES)],
        )
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
    # A harmless change upstream inside the lookback: the hardest decoy. Not for
    # abstain cases, where it would make a cause look supportable.
    candidates = [role for role in upstream if role not in causal_roles]
    if family.outcome == "diagnose" and candidates and rng.random() < 0.3:
        at = failure - timedelta(minutes=rng.randint(30, 20 * 60))
        deployment(
            bench,
            domain,
            at,
            names[rng.choice(candidates)],
            [rng.choice(HARMLESS_CHANGES)],
        )

    # Logs: normal work, the errors, the family's own clues, and a symptom.
    earliest = min([0, *(offset for _, _, _, offset in family.extra_logs)])
    start = failure - timedelta(minutes=rng.randint(10, 40))
    start = min(start, failure + timedelta(minutes=earliest - 5)).replace(second=0)
    end = max(start + timedelta(hours=2), failure + timedelta(hours=1))
    log(
        bench,
        domain,
        start + timedelta(minutes=2),
        failing,
        "INFO",
        "Processed a batch normally",
    )
    error_ids = []
    at = failure
    for _ in range(rng.randint(2, 4)):
        error_ids.append(
            log(
                bench,
                domain,
                at,
                failing,
                "ERROR",
                fill(family.error),
                family.exception,
            )
        )
        at += timedelta(seconds=rng.randint(20, 300))
    relevant = error_ids[1:]
    for role, level, message, offset in family.extra_logs:
        relevant.append(
            log(
                bench,
                domain,
                failure + timedelta(minutes=offset),
                names[role],
                level,
                fill(message),
            )
        )
    if family.symptom:
        role, message = family.symptom
        relevant.append(
            log(
                bench,
                domain,
                failure + timedelta(minutes=rng.randint(5, 30)),
                names[role],
                "WARN",
                fill(message),
            )
        )

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
            raise ValueError(f"{family.code} rolls back a deployment it doesn't have")
        plan.append({"action": action, "target": resolved})
    bench.truths[incident_id] = {
        "incident_id": incident_id,
        "split": family.split,
        "family": family.name,
        "expected_outcome": family.outcome,
        "category": family.category,
        "root_cause": fill(family.root_cause),
        "required_evidence_ids": [error_ids[0], *change_ids[:1]],
        "relevant_evidence_ids": [
            *relevant,
            *change_ids[1:],
            documents["api_spec"],
            documents["runbook"],
            documents["historical_incident"],
            map_id,
        ],
        "acceptable_remediations": [fill(text) for text in family.acceptable],
        "unsafe_actions": [fill(text) for text in family.unsafe],
        "expected_approval_required": family.outcome == "diagnose" and family.approval,
        "reference_plan": plan,
    }


def schedule(
    rng: random.Random,
    dev_variants: int = DEV_VARIANTS,
    test_cases: int = TEST_CASES,
    development: bool = False,
) -> list[Family]:
    if development:
        # Every family, dev and test alike, with the same number of variants.
        order = [family for family in FAMILIES for _ in range(dev_variants)]
        rng.shuffle(order)
        return order
    dev = [family for family in FAMILIES if family.split == "dev"]
    test = [family for family in FAMILIES if family.split == "test"]
    order = [family for family in dev for _ in range(dev_variants)]
    base, extra = divmod(test_cases, len(test))
    for index, family in enumerate(test):
        order += [family] * (base + (1 if index < extra else 0))
    rng.shuffle(order)
    return order


def generate(
    seed: int,
    dev_variants: int = DEV_VARIANTS,
    test_cases: int = TEST_CASES,
    development: bool = False,
) -> Benchmark:
    """Writes the benchmark's incidents.

    With development, every family gets dev_variants variants, and every incident
    is marked dev: a set for working on FlowGuard once the test families have been
    run, since a family's failures, once seen, make it tuning data.
    """
    rng = random.Random(seed)
    systems = {domain: system(domain, rng) for domain in DOMAINS}
    bench = Benchmark()
    order = schedule(rng, dev_variants, test_cases, development)
    for index, family in enumerate(order, start=1):
        info = systems[rng.choice(DOMAINS)]
        add_incident(bench, rng, index, family, info, START + SPACING * (index - 1))
    if development:
        for truth in bench.truths.values():
            truth["split"] = "dev"
    return bench


def write(bench: Benchmark, out: Path, seed: int, options: str = "") -> None:
    if out.exists():
        shutil.rmtree(out)

    def dump(relative: str, value: Any) -> None:
        path = out / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

    for domain, records in bench.logs.items():
        path = out / "logs" / f"{domain}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        ordered = sorted(records, key=lambda record: record["timestamp"])
        path.write_text(
            "".join(json.dumps(r) + "\n" for r in ordered), encoding="utf-8"
        )
    for folder, groups in (
        ("deployments", bench.deployments),
        ("alerts", bench.alerts),
        ("metrics", bench.metrics),
    ):
        for domain, records in groups.items():
            dump(f"{folder}/{domain}.json", records)
    for domain, dependency_map in bench.maps.items():
        dump(f"dependency_maps/{domain}.json", dependency_map)
    for relative, text in bench.documents.items():
        path = out / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    for incident_id, incident in bench.incidents.items():
        dump(f"incidents/{incident_id}.json", incident)
        dump(f"ground_truth/{incident_id}.json", bench.truths[incident_id])
    (out / "README.md").write_text(
        "# FlowGuard benchmark\n\n"
        f"Generated by `python -m flowguard.benchmark.generate --seed {seed}{options}`. "
        "Don't edit by hand: change the families or the generator, and regenerate.\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate FlowGuard's benchmark.")
    parser.add_argument("--out", type=Path, default=Path("data/benchmark"))
    parser.add_argument("--seed", type=int, default=2027)
    parser.add_argument(
        "--development",
        action="store_true",
        help="give every family --dev-variants variants, all marked dev",
    )
    parser.add_argument("--dev-variants", type=int, default=DEV_VARIANTS)
    parser.add_argument("--test-cases", type=int, default=TEST_CASES)
    arguments = parser.parse_args()
    bench = generate(
        arguments.seed,
        arguments.dev_variants,
        arguments.test_cases,
        arguments.development,
    )
    options = (
        f" --out {arguments.out.as_posix()} --development --dev-variants {arguments.dev_variants}"
        if arguments.development
        else ""
    )
    write(bench, arguments.out, arguments.seed, options)
    splits: dict[str, int] = defaultdict(int)
    for truth in bench.truths.values():
        splits[truth["split"]] += 1
    print(
        f"{len(bench.incidents)} incidents written to {arguments.out}: {dict(splits)}"
    )


if __name__ == "__main__":
    main()
