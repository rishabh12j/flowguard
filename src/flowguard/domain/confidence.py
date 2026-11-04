from collections.abc import Mapping

from flowguard.domain.causality import came_before, services_at_or_upstream
from flowguard.domain.evidence import EvidenceItem
from flowguard.domain.hypotheses import ProposedHypothesis

# The brief's starting rubric. Tune it with the evaluation runner, not by hand.
DIRECT_ERROR = 0.30
TIMELINE = 0.20
DEPENDENCY_PATH = 0.15
API_OR_SCHEMA = 0.15
DEPLOYMENT = 0.10
HISTORICAL_MATCH = 0.10
PER_CONTRADICTION = 0.20
PER_MISSING_SOURCE = 0.15


def score(
    hypothesis: ProposedHypothesis,
    evidence: Mapping[str, EvidenceItem],
    first_failure: EvidenceItem | None,
    missing_sources: int,
) -> tuple[float, str]:
    cited = [
        evidence[evidence_id] for evidence_id in hypothesis.supporting_evidence_ids
    ]
    deployments = [item for item in cited if item.source_type == "deployment"]
    maps = [item for item in evidence.values() if item.source_type == "dependency_map"]

    timeline = path = False
    if first_failure is not None:
        timeline = any(came_before(item, first_failure) for item in deployments)
        upstream: set[str] = set()
        for dependency_map in maps:
            upstream |= services_at_or_upstream(
                dependency_map, first_failure.source_name
            )
        path = any(item.source_name in upstream for item in deployments)

    signals = [
        (
            DIRECT_ERROR,
            "cites an error log",
            any(
                item.source_type == "log" and item.metadata.get("level") == "ERROR"
                for item in cited
            ),
        ),
        (TIMELINE, "a cited deployment came before the first failure", timeline),
        (DEPENDENCY_PATH, "a cited deployment is upstream of the failure", path),
        (
            API_OR_SCHEMA,
            "cites an API specification",
            any(item.source_type == "api_spec" for item in cited),
        ),
        (DEPLOYMENT, "cites a deployment", bool(deployments)),
        (
            HISTORICAL_MATCH,
            "cites a similar past incident",
            any(item.source_type == "historical_incident" for item in cited),
        ),
    ]

    total = 0.0
    reasons = []
    for points, reason, present in signals:
        if present:
            total += points
            reasons.append(f"+{points:.2f} {reason}")

    contradictions = len(hypothesis.contradicting_evidence_ids)
    if contradictions:
        total -= PER_CONTRADICTION * contradictions
        reasons.append(
            f"-{PER_CONTRADICTION * contradictions:.2f} contradicting evidence"
        )
    if missing_sources:
        total -= PER_MISSING_SOURCE * missing_sources
        reasons.append(f"-{PER_MISSING_SOURCE * missing_sources:.2f} missing evidence")

    # Sums like 0.30 - 0.20 come out as 0.0999..., so round before comparing to a threshold.
    confidence = round(min(max(total, 0.0), 1.0), 2)
    return confidence, "; ".join(reasons) or "no supporting signals"
