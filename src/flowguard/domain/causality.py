from datetime import timedelta

from flowguard.domain.evidence import EvidenceItem

# A deployment can cause failures long after it finishes, so look back a full day.
LOOKBACK = timedelta(hours=24)


def services_at_or_upstream(dependency_map: EvidenceItem, service: str) -> set[str]:
    edges = dependency_map.metadata["edges"]
    found = {service}
    frontier = {service}
    while frontier:
        frontier = {edge["from"] for edge in edges if edge["to"] in frontier} - found
        found |= frontier
    return found


def came_before(change: EvidenceItem, failure: EvidenceItem) -> bool:
    """True when a change happened before a failure, within the lookback."""
    if change.timestamp is None or failure.timestamp is None:
        return False
    return timedelta(0) < failure.timestamp - change.timestamp <= LOOKBACK
