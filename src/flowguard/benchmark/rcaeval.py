"""Convert RCAEval RE3 cases into FlowGuard's incident format.

RCAEval (Pham et al., 2025; https://github.com/phamquiluan/RCAEval) publishes
failure cases recorded on three open-source microservice systems, with real logs,
metrics and traces, under CC BY 4.0. In RE3, each case is one code-level fault
injected into one service: incorrect parameter values (f1), missing parameters
(f2), a missing function call (f3), incorrect return values (f4) or a missing
exception handler (f5). The label is the faulty service.

A case holds tens of thousands of log lines, and FlowGuard's log search returns at
most 50 lines to a model with an 8,192-token context. So this does what a log
platform's pattern view does: it groups each service's messages into patterns,
counts each pattern before and after the incident's start, and keeps the patterns
that matter most, one line each with its counts. Errors and warnings after the
start come first, then patterns that only appear after it, then errors that
stopped. The same rules apply to every case; they were set on Sock Shop, the
development system, before any other system was converted.

What is kept from each case: logs only, in a window from 5 minutes before the
injection to 10 minutes after. Metrics are left out. The dependency map comes
from Sock Shop's published architecture, which has no traces, or from the calls
traced before each injection.

Run: python -m flowguard.benchmark.rcaeval --raw data/external/rcaeval-re3/raw
     --system SS --split dev --out data/external/rcaeval-re3/sock-shop
"""

import argparse
import csv
import json
import re
import sys
from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Literal

from flowguard.seed_schemas import DependencyMapRecord, GroundTruth, LogRecord

# Some messages are whole stack traces.
csv.field_size_limit(sys.maxsize if sys.maxsize < 2**31 else 2**31 - 1)

SYSTEMS = {"OB": "online-boutique", "SS": "sock-shop", "TT": "train-ticket"}
FAULTS = {
    "f1": "incorrect parameter values",
    "f2": "missing parameters",
    "f3": "a missing function call",
    "f4": "incorrect return values",
    "f5": "a missing exception handler",
}

BEFORE = timedelta(minutes=5)
AFTER = timedelta(minutes=10)
MAX_LINES = 45  # under the log search's 50, so nothing is cut off
# Lines kept per service, by kind: errors and warnings after the start, other new
# patterns after it, and errors that stopped at it.
PER_SERVICE = {"active_errors": 4, "new_patterns": 2, "stopped_errors": 1}
MAX_NEW_PATTERNS = 15
MESSAGE_LINES = 4
MESSAGE_CHARS = 500
# The log text kept per case, counting about 90 characters of heading per line, so
# that both questions fit Gemma's 8,192-token context with the prompts and the map.
CASE_CHARS = 14_000
LINE_HEADING = 90

Level = Literal["DEBUG", "INFO", "WARN", "ERROR"]

# --------------------------------------------------------------------- reading


EXPLICIT_LEVEL = re.compile(
    r"\b(TRACE|DEBUG|INFO|WARN|WARNING|ERROR|FATAL|SEVERE|CRITICAL)\b"
)
JSON_LEVEL = re.compile(r'"(?:level|severity)"\s*:\s*"(\w+)"', re.IGNORECASE)
MONGO_LEVEL = re.compile(r'"s"\s*:\s*"([FEWID])\d?"')
ERROR_WORDS = re.compile(
    r"(?i)\b(error|exception|traceback|panic|fatal|fail(?:ed|ure|s)?|refused"
    r"|unavailable|timed?\s?out)\b|\bstatus(?:code)?\W{0,3}5\d\d\b"
    # An access-log line for a request that failed on the server: "POST /cart 500".
    r"|\b(?:GET|POST|PUT|PATCH|DELETE)\s+\S+\s+5\d\d\b"
)
LEVELS: dict[str, Level] = {
    "TRACE": "DEBUG",
    "DEBUG": "DEBUG",
    "D": "DEBUG",
    "INFO": "INFO",
    "I": "INFO",
    "WARN": "WARN",
    "WARNING": "WARN",
    "W": "WARN",
    "ERROR": "ERROR",
    "E": "ERROR",
    "FATAL": "ERROR",
    "F": "ERROR",
    "SEVERE": "ERROR",
    "CRITICAL": "ERROR",
}


def infer_level(message: str) -> Level:
    """The level a message states, or ERROR when it reads as a failure. RE3's logs
    have no level column, and each service formats its own."""
    for pattern in (JSON_LEVEL, MONGO_LEVEL):
        found = pattern.search(message)
        if found and found.group(1).upper() in LEVELS:
            return LEVELS[found.group(1).upper()]
    found = EXPLICIT_LEVEL.search(message[:80])
    if found:
        return LEVELS[found.group(1)]
    return "ERROR" if ERROR_WORDS.search(message) else "INFO"


EXCEPTION = re.compile(r"\b([A-Za-z_][\w.$]*(?:Exception|Error))\b")


def exception_type(message: str) -> str | None:
    found = EXCEPTION.search(message)
    return found.group(1) if found else None


LEADING_TIME = re.compile(
    r"^\s*(?:\d{4}-\d\d-\d\d[ T][\d:.,]+(?:Z|[+-]\d\d:?\d\d)?|\d\d:\d\d:\d\d[.,\d]*)\s*"
)
SUBSTITUTIONS = (
    (re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F-]{27,}"), "<uuid>"),
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "<email>"),
    (re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}(?::\d+)?\b"), "<ip>"),
    # A token mixing letters and digits, such as an ID, a hash or a cookie.
    (re.compile(r"\b(?=\w*\d)\w{6,}\b"), "<id>"),
    (re.compile(r"\d+"), "<n>"),
)


def template(message: str) -> str:
    """The message's pattern: its first line, without the values that vary."""
    lines = [line for line in message.splitlines() if line.strip()]
    text = LEADING_TIME.sub("", lines[0] if lines else "")
    for pattern, placeholder in SUBSTITUTIONS:
        text = pattern.sub(placeholder, text)
    return re.sub(r"\s+", " ", text).strip()[:200]


def shortened(message: str) -> str:
    lines = [line.rstrip() for line in message.splitlines() if line.strip()]
    text = "\n".join(lines[:MESSAGE_LINES])
    if len(lines) > MESSAGE_LINES:
        text += "\n..."
    return text if len(text) <= MESSAGE_CHARS else text[: MESSAGE_CHARS - 3] + "..."


@dataclass
class Pattern:
    service: str
    template: str
    level: Level
    before: int = 0
    after: int = 0
    first_before: datetime | None = None
    first_after: datetime | None = None
    example_before: str = ""
    example_after: str = ""

    def add(self, when: datetime, message: str, started: datetime) -> None:
        if when < started:
            self.before += 1
            if self.first_before is None or when < self.first_before:
                self.first_before, self.example_before = when, message
        else:
            self.after += 1
            if self.first_after is None or when < self.first_after:
                self.first_after, self.example_after = when, message


def read_patterns(case: Path, started: datetime) -> dict[tuple[str, str], Pattern]:
    patterns: dict[tuple[str, str], Pattern] = {}
    with open(case / "logs.csv", newline="", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            when = datetime.fromtimestamp(int(row["timestamp"]) / 1e9, UTC)
            if not started - BEFORE <= when <= started + AFTER:
                continue
            message = row["message"] or ""
            if not message.strip():
                continue
            service = row["container_name"]
            key = (service, template(message))
            if key not in patterns:
                patterns[key] = Pattern(service, key[1], infer_level(message))
            patterns[key].add(when, message, started)
    return patterns


# ------------------------------------------------------------------- selecting


def select(patterns: dict[tuple[str, str], Pattern]) -> list[Pattern]:
    """The patterns that matter most, within MAX_LINES."""
    found = list(patterns.values())
    problems = ("ERROR", "WARN")
    active = sorted(
        (p for p in found if p.level in problems and p.after),
        key=lambda p: (p.before > 0, -p.after, p.service, p.template),
    )
    new = sorted(
        (p for p in found if p.level not in problems and p.after and not p.before),
        key=lambda p: (-p.after, p.service, p.template),
    )
    stopped = sorted(
        (p for p in found if p.level in problems and p.before and not p.after),
        key=lambda p: (-p.before, p.service, p.template),
    )
    chosen: list[Pattern] = []
    for kind, group, limit in (
        ("active_errors", active, MAX_LINES),
        ("new_patterns", new, MAX_NEW_PATTERNS),
        ("stopped_errors", stopped, MAX_LINES),
    ):
        taken: Counter[str] = Counter()
        for pattern in group:
            if len(chosen) >= MAX_LINES or sum(taken.values()) >= limit:
                break
            if taken[pattern.service] < PER_SERVICE[kind]:
                taken[pattern.service] += 1
                chosen.append(pattern)
    return chosen


def clock(when: datetime) -> str:
    return when.strftime("%H:%M")


def summary(pattern: Pattern, started: datetime) -> str:
    return (
        f"[this pattern: {pattern.after} times from {clock(started)} to "
        f"{clock(started + AFTER)}, {pattern.before} times from "
        f"{clock(started - BEFORE)} to {clock(started)}]"
    )


def log_line(pattern: Pattern, started: datetime) -> dict[str, Any]:
    # A pattern is shown when it was first seen in the window, as a log platform's
    # pattern view does, so one that was already there before the start shows so.
    if pattern.first_before is not None:
        when, example = pattern.first_before, pattern.example_before
    else:
        assert pattern.first_after is not None
        when, example = pattern.first_after, pattern.example_after
    return {
        "timestamp": when,
        "service": pattern.service,
        "level": pattern.level,
        "message": f"{shortened(example)}\n{summary(pattern, started)}",
        "exception_type": exception_type(example),
        "metadata": {"count_after": pattern.after, "count_before": pattern.before},
    }


def within_budget(lines: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The lines, in order of importance, up to CASE_CHARS."""
    kept, used = [], 0
    for line in lines:
        used += len(line["message"]) + LINE_HEADING
        if used > CASE_CHARS:
            break
        kept.append(line)
    return kept


# ------------------------------------------------------------ dependency maps

# Sock Shop's published architecture (github.com/microservices-demo), as RE3-SS
# has no traces. An edge from A to B means B depends on A.
SOCK_SHOP_NODES = {
    "front-end": "api",
    "catalogue": "service",
    "carts": "service",
    "orders": "service",
    "payment": "service",
    "shipping": "service",
    "user": "service",
    "queue-master": "service",
    "catalogue-db": "database",
    "carts-db": "database",
    "orders-db": "database",
    "user-db": "database",
    "session-db": "database",
    "rabbitmq": "queue",
}
SOCK_SHOP_EDGES = [
    ("catalogue", "front-end"),
    ("carts", "front-end"),
    ("orders", "front-end"),
    ("user", "front-end"),
    ("session-db", "front-end"),
    ("carts", "orders"),
    ("user", "orders"),
    ("payment", "orders"),
    ("shipping", "orders"),
    ("catalogue-db", "catalogue"),
    ("carts-db", "carts"),
    ("orders-db", "orders"),
    ("user-db", "user"),
    ("shipping", "rabbitmq"),
    ("rabbitmq", "queue-master"),
]


def node_type(name: str) -> str:
    lowered = name.lower()
    if any(word in lowered for word in ("mongo", "redis", "-db", "mysql")):
        return "database"
    if any(word in lowered for word in ("rabbit", "kafka", "queue")):
        return "queue"
    return "service"


def traced_calls(case: Path, started: datetime) -> set[tuple[str, str]]:
    """Calls between services traced before the injection, as (callee, caller):
    the callee's answers flow to the caller."""
    spans: dict[str, str] = {}
    parents: list[tuple[str, str]] = []
    cutoff = started.timestamp() * 1000
    with open(case / "traces.csv", newline="", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            if float(row["startTimeMillis"] or 0) >= cutoff:
                continue
            if "opentelemetry" in (row.get("operationName") or ""):
                continue
            spans[row["spanID"]] = row["serviceName"]
            if row.get("parentSpanID"):
                parents.append((row["spanID"], row["parentSpanID"]))
    return {
        (spans[child], spans[parent])
        for child, parent in parents
        if parent in spans and spans[child] != spans[parent]
    }


def dependency_map(
    system: str, calls: set[tuple[str, str]] | None
) -> DependencyMapRecord:
    if calls is None:
        nodes = SOCK_SHOP_NODES
        edges = SOCK_SHOP_EDGES
    else:
        names = sorted({name for call in calls for name in call})
        nodes = {name: node_type(name) for name in names}
        edges = sorted(calls)
    return DependencyMapRecord.model_validate(
        {
            "map_id": f"DEPMAP-{system.upper()}",
            "system": system,
            "nodes": [{"name": n, "type": t} for n, t in nodes.items()],
            "edges": [{"from": a, "to": b} for a, b in edges],
        }
    )


# ------------------------------------------------------------------ converting


@dataclass
class Case:
    path: Path
    service: str
    fault: str
    started: datetime
    lines: list[dict[str, Any]] = field(default_factory=list)


CASE_NAME = re.compile(r"^(?P<service>.+)_(?P<fault>f\d)(?:_\d+)?$")


def cases_in(raw: Path, code: str) -> Iterator[Case]:
    for folder in sorted((raw / f"RE3-{code}").iterdir()):
        named = CASE_NAME.match(folder.name)
        if not named:
            raise ValueError(f"unexpected case folder: {folder}")
        for run in sorted(p for p in folder.iterdir() if p.is_dir()):
            injected = int((run / "inject_time.txt").read_text().strip())
            yield Case(
                run,
                named["service"],
                named["fault"],
                datetime.fromtimestamp(injected, UTC),
            )


def convert(raw: Path, code: str, split: str, out: Path) -> int:
    system = SYSTEMS[code]
    cases = sorted(cases_in(raw, code), key=lambda c: c.started)
    for earlier, later in zip(cases, cases[1:], strict=False):
        if earlier.started + AFTER >= later.started - BEFORE:
            raise ValueError(f"{earlier.path} and {later.path} overlap in time")
    calls: set[tuple[str, str]] | None = None if code == "SS" else set()
    for case in cases:
        case.lines = within_budget(
            [
                log_line(p, case.started)
                for p in select(read_patterns(case.path, case.started))
            ]
        )
        if calls is not None:
            calls |= traced_calls(case.path, case.started)

    for folder in ("incidents", "ground_truth", "logs", "dependency_maps"):
        (out / folder).mkdir(parents=True, exist_ok=True)
    number = 0
    records = []
    for index, case in enumerate(cases, start=1):
        incident_id = f"RE3-{code}-{index:03d}"
        ids = []
        for line in sorted(case.lines, key=lambda line: line["timestamp"]):
            number += 1
            event_id = f"LOG-{number:05d}"
            ids.append((event_id, line))
            records.append(
                LogRecord.model_validate(
                    {
                        "event_id": event_id,
                        "environment": "rcaeval-testbed",
                        "correlation_id": f"CORR-{event_id}",
                        **line,
                    }
                )
            )
        write_case(out, incident_id, system, split, case, ids)
    with open(out / "logs" / f"{system}.jsonl", "w", encoding="utf-8") as f:
        for record in records:
            f.write(record.model_dump_json() + "\n")
    (out / "dependency_maps" / f"{system}.json").write_text(
        dependency_map(system, calls).model_dump_json(by_alias=True, indent=2) + "\n",
        encoding="utf-8",
    )
    (out / "README.md").write_text(README.format(system=system), encoding="utf-8")
    return len(cases)


def write_case(
    out: Path,
    incident_id: str,
    system: str,
    split: str,
    case: Case,
    ids: list[tuple[str, dict[str, Any]]],
) -> None:
    started = case.started.replace(second=0)
    incident = {
        "incident_id": incident_id,
        "description": (
            f"Users of {system} report errors and failed requests since about "
            f"{clock(started)} UTC."
        ),
        "affected_system": system,
        "start_time": (case.started - BEFORE).isoformat().replace("+00:00", "Z"),
        "end_time": (case.started + AFTER).isoformat().replace("+00:00", "Z"),
    }
    faulty = [i for i, line in ids if line["service"] == case.service]
    after = [i for i, line in ids if line["timestamp"] >= case.started]
    required = [i for i in faulty if i in after] or faulty or after[:1] or [ids[0][0]]
    truth = GroundTruth.model_validate(
        {
            "incident_id": incident_id,
            "split": split,
            "family": f"{case.service}_{case.fault}",
            "expected_outcome": "diagnose",
            # A code fault released into a service is a release broken in itself.
            "category": "deployment_or_configuration",
            "root_cause": (
                f"A code-level fault, {FAULTS[case.fault]}, was released into "
                f"{case.service} (RCAEval RE3, {case.path.parent.name}/{case.path.name})."
            ),
            "root_cause_service": case.service,
            "required_evidence_ids": required,
            "relevant_evidence_ids": [i for i in after if i not in required],
            "acceptable_remediations": [
                f"Roll back the faulty release of {case.service}"
            ],
            "unsafe_actions": [],
            "expected_approval_required": True,
            # RE3 has no plans; plan metrics aren't reported for these incidents.
            "reference_plan": [
                {"action": "notify_service_owner", "target": case.service}
            ],
        }
    )
    (out / "incidents" / f"{incident_id}.json").write_text(
        json.dumps(incident, indent=2) + "\n", encoding="utf-8"
    )
    (out / "ground_truth" / f"{incident_id}.json").write_text(
        truth.model_dump_json(indent=2, exclude_none=True) + "\n", encoding="utf-8"
    )


README = """# RCAEval RE3: {system}

Converted from RCAEval (Pham et al., "RCAEval: A Benchmark for Root Cause Analysis
of Microservice Systems with Telemetry Data", 2025), dataset RE3, published on
Zenodo (https://doi.org/10.5281/zenodo.14590730) under CC BY 4.0. Converted by
`python -m flowguard.benchmark.rcaeval`: logs condensed to patterns with counts,
and a dependency map. Not redistributed in this repository.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--system", choices=sorted(SYSTEMS), required=True)
    parser.add_argument("--split", choices=["dev", "test"], required=True)
    parser.add_argument("--out", type=Path, required=True)
    arguments = parser.parse_args()
    count = convert(arguments.raw, arguments.system, arguments.split, arguments.out)
    print(f"Converted {count} cases to {arguments.out}")


if __name__ == "__main__":
    main()
