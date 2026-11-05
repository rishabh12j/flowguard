"""A readable report of one investigation, built from its audit record."""

from collections import Counter

from flowguard.domain.audit import InvestigationRecord

STATUS_MEANING = {
    "diagnosed": "Diagnosed. The plan changes nothing, so it needs no approval.",
    "abstained": "No root cause was confident enough to report.",
    "rejected": "The request was invalid, so nothing was investigated.",
    "awaiting_approval": "Waiting for a person to approve the plan.",
    "approved": "The plan was approved.",
    "declined": "The plan was declined.",
    "more_evidence_requested": "A reviewer asked for more evidence.",
}


def render_report(record: InvestigationRecord) -> str:
    incident = record.incident
    title = (
        f"{incident.incident_id}: {record.category}" if incident else "Rejected request"
    )
    lines = [
        f"# {title}",
        "",
        f"{STATUS_MEANING[record.status]} Investigation `{record.investigation_id}`, "
        f"record version {record.version}.",
    ]
    if incident:
        lines += [
            "",
            f"**Incident:** {incident.description}",
            f"**System:** `{incident.affected_system}`, "
            f"{incident.start_time:%Y-%m-%d %H:%M} to {incident.end_time:%H:%M} UTC.",
        ]

    selected = next(
        (
            h
            for h in record.hypotheses
            if h.hypothesis_id == record.selected_hypothesis_id
        ),
        None,
    )
    if selected:
        lines += [
            "",
            "## Root cause",
            "",
            f"{selected.description} ({selected.category}, confidence "
            f"{selected.confidence:.2f})",
            "",
            f"- **Why this confidence:** {selected.confidence_reason}",
            f"- **Evidence:** {', '.join(selected.supporting_evidence_ids)}",
        ]
    others = [h for h in record.hypotheses if h is not selected]
    if others:
        lines += ["", "Other hypotheses considered:", ""]
        lines += [
            f"- {h.description} ({h.category}, confidence {h.confidence:.2f})"
            for h in others
        ]
    if record.abstention:
        lines += [
            "",
            "## No conclusion",
            "",
            f"FlowGuard abstained: {record.abstention}.",
        ]

    if record.actions:
        lines += ["", "## Plan", ""]
        for action in record.actions:
            approval = (
                "needs approval" if action.requires_approval else "no approval needed"
            )
            lines += [
                f"{action.step}. **{action.action}** on `{action.target}`: "
                f"{action.risk} risk, {approval}.",
                f"   - Why: {action.reason} ({', '.join(action.evidence_ids)})",
                f"   - Verify: {action.verification}",
            ]
            if action.rollback:
                lines.append(f"   - Roll back: {action.rollback}")
    if record.rejected_actions:
        lines += ["", "Refused by validation:", ""]
        lines += [
            f"- {item.proposed.action} on `{item.proposed.target}`: {item.problem}"
            for item in record.rejected_actions
        ]

    if record.decision:
        decision = record.decision
        lines += [
            "",
            "## Decision",
            "",
            f"{decision.decision} by {decision.approver} at "
            f"{decision.decided_at:%Y-%m-%d %H:%M} UTC."
            + (f" Comment: {decision.comment}" if decision.comment else ""),
        ]
    if record.reviewer_request:
        lines += ["", f"A reviewer asked for more evidence: {record.reviewer_request}"]

    if record.errors:
        lines += ["", "## Problems while investigating", ""]
        lines += [f"- {error}" for error in record.errors]

    outcomes = Counter(call.outcome for call in record.tool_calls)
    lines += [
        "",
        "## Audit",
        "",
        f"{len(record.tool_calls)} tool calls ("
        + ", ".join(f"{count} {outcome}" for outcome, count in sorted(outcomes.items()))
        + f"). {len(record.evidence_ids)} pieces of evidence gathered. "
        f"Started {record.started_at:%Y-%m-%d %H:%M:%S} UTC, this version saved "
        f"{record.finished_at:%Y-%m-%d %H:%M:%S} UTC.",
        "",
    ]
    return "\n".join(lines)
