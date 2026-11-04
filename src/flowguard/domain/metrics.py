from datetime import datetime
from typing import Any

from flowguard.domain.evidence import EvidenceItem


def metric_evidence(
    *,
    series_id: str,
    service: str,
    metric: str,
    unit: str,
    threshold: float,
    points: list[dict[str, Any]],
) -> EvidenceItem | None:
    """One metric over a period, as evidence. None when the period has no points.

    The timestamp is when the metric first went above its threshold, which is
    the moment it became a change worth explaining. A metric that stayed below
    its threshold has no timestamp, so it can't count as a cause in time.
    """
    if not points:
        return None
    crossing = next((point for point in points if point["value"] > threshold), None)
    peak = max(points, key=lambda point: point["value"])
    summary = (
        f"{metric} for {service} peaked at {peak['value']} {unit} at "
        f"{peak['timestamp']}, against a threshold of {threshold}. "
    )
    summary += (
        f"It first went above the threshold at {crossing['timestamp']}."
        if crossing
        else "It stayed below the threshold."
    )
    return EvidenceItem(
        evidence_id=series_id,
        source_type="metric",
        source_name=service,
        timestamp=crossing["timestamp"] if crossing else None,
        title=f"{service} {metric}",
        content=summary,
        metadata={
            "metric": metric,
            "unit": unit,
            "threshold": threshold,
            "points": points,
        },
    )


def within(item: EvidenceItem, start: datetime, end: datetime) -> EvidenceItem | None:
    """The same metric, summarised over a shorter period."""
    points = [
        point
        for point in item.metadata["points"]
        if start <= datetime.fromisoformat(point["timestamp"]) <= end
    ]
    return metric_evidence(
        series_id=item.evidence_id,
        service=item.source_name,
        metric=item.metadata["metric"],
        unit=item.metadata["unit"],
        threshold=item.metadata["threshold"],
        points=points,
    )
