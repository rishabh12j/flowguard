"""What changed in the logs when the failure began, worked out by code.

A model shown raw log lines has to work out for itself which errors are new and
which were always there. On RCAEval's Sock Shop cases Gemma got that wrong in 22
of 30: it blamed a service that logs the same error all day. So code does it.

A connector that can count gives each log pattern two counts: how often it
appeared in a stretch before the reported start of the failure, and how often
since (metadata count_before, count_after, minutes_before, minutes_after). From
those, each pattern is new, increased, steady (background) or stopped. A log line
without counts has no signal, and nothing here applies to it.

The candidates for where the cause lies are the services with a new or increased
error or warning, deepest in the dependency map first: a service that others call
can cause their errors, and not the other way round.

Known limits. A reported start that is wrong shifts the comparison. A cause that
began before the stretch counted looks like background. A harmless release makes
new patterns too. And a service that fails silently is never a candidate.
"""

from collections.abc import Iterable
from typing import Literal

from flowguard.domain.evidence import EvidenceItem

Kind = Literal["new", "increased", "steady", "stopped"]

# A pattern has increased when its rate since the start is more than this many
# times its rate before. Chosen before any run; not tuned.
INCREASE = 2.0
PROBLEMS = ("ERROR", "WARN")
COUNTS = ("count_before", "count_after", "minutes_before", "minutes_after")


def kind_of(item: EvidenceItem) -> Kind | None:
    """The signal of one log pattern, or None when it carries no counts."""
    if item.source_type != "log" or any(k not in item.metadata for k in COUNTS):
        return None
    before, after = item.metadata["count_before"], item.metadata["count_after"]
    if not after:
        return "stopped"
    if not before:
        return "new"
    rate_before = before / item.metadata["minutes_before"]
    rate_after = after / item.metadata["minutes_after"]
    return "increased" if rate_after > INCREASE * rate_before else "steady"


def minutes(value: float) -> str:
    return f"{value:g} minutes"


def describe(item: EvidenceItem) -> str | None:
    """The signal in words, for the model to read beside the log line."""
    kind = kind_of(item)
    if kind is None:
        return None
    m = item.metadata
    before = f"{m['count_before']} times in the {minutes(m['minutes_before'])} before"
    after = f"{m['count_after']} times in the {minutes(m['minutes_after'])} since"
    if kind == "new":
        return f"new since the failure began: {after}, never before"
    if kind == "increased":
        return f"increased since the failure began: {after}, {before}"
    if kind == "stopped":
        return f"stopped when the failure began: {before}, none since"
    return f"background, about as frequent before the failure began: {before}, {after}"


def callees(evidence: Iterable[EvidenceItem]) -> dict[str, set[str]]:
    """Each service's direct dependencies. A map's edge from A to B means B
    depends on A."""
    found: dict[str, set[str]] = {}
    for item in evidence:
        if item.source_type == "dependency_map":
            for edge in item.metadata.get("edges", ()):
                found.setdefault(edge["to"], set()).add(edge["from"])
    return found


def below(service: str, calls: dict[str, set[str]]) -> set[str]:
    """Everything the service depends on, directly or through others."""
    seen: set[str] = set()
    queue = [service]
    while queue:
        for callee in calls.get(queue.pop(), ()):
            if callee not in seen:
                seen.add(callee)
                queue.append(callee)
    return seen - {service}


def candidates(evidence: Iterable[EvidenceItem]) -> list[str] | None:
    """The services with a new or increased error or warning, deepest first. None
    when no log carries counts, so nothing can be said about what changed."""
    items = list(evidence)
    kinds = [(item, kind_of(item)) for item in items]
    if all(kind is None for _, kind in kinds):
        return None
    found = {
        item.source_name
        for item, kind in kinds
        if kind in ("new", "increased") and item.metadata.get("level") in PROBLEMS
    }
    calls = callees(items)
    return sorted(found, key=lambda s: (len(below(s, calls) & found), s))


def deepest(evidence: Iterable[EvidenceItem]) -> list[str]:
    """The candidates that depend on no other candidate."""
    items = list(evidence)
    found = candidates(items) or []
    calls = callees(items)
    return [s for s in found if not below(s, calls) & set(found)]
