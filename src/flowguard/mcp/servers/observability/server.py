from collections.abc import Sequence
from datetime import datetime

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations
from pydantic import AwareDatetime, BaseModel

from flowguard.dataset import load_evidence
from flowguard.domain.evidence import EvidenceItem
from flowguard.domain.metrics import within

MAX_RESULTS = 50

# The seeded data, used when a server isn't given its own.
EVIDENCE = load_evidence()


class LogSearchResult(BaseModel):
    items: list[EvidenceItem]
    truncated: bool


class AlertResult(BaseModel):
    items: list[EvidenceItem]


class MetricResult(BaseModel):
    items: list[EvidenceItem]


def log_time(item: EvidenceItem) -> datetime:
    if item.timestamp is None:
        raise ValueError(f"{item.evidence_id} has no timestamp")
    return item.timestamp


fired_at = log_time


def matches_query(item: EvidenceItem, query: str) -> bool:
    searchable = f"{item.content} {item.metadata}".lower()
    return query.lower() in searchable


def create_server(evidence: Sequence[EvidenceItem] | None = None) -> MCPServer:
    """The observability server, over the given evidence or the seeded data."""
    source = EVIDENCE if evidence is None else evidence
    logs = [item for item in source if item.source_type == "log"]
    alerts = [item for item in source if item.source_type == "alert"]
    metrics = [item for item in source if item.source_type == "metric"]
    server = MCPServer("observability-server")

    @server.tool(annotations=ToolAnnotations(read_only_hint=True))
    def search_logs(
        start_time: AwareDatetime,
        end_time: AwareDatetime,
        service: str | None = None,
        query: str | None = None,
        correlation_id: str | None = None,
    ) -> LogSearchResult:
        """Search application logs within a required time range.

        Results are sorted oldest first. Filter by service, by correlation_id to
        follow one transaction across services, or by query. The query is
        case-insensitive and also searches metadata such as invoice IDs and
        exception types. An empty result means no logs matched. If truncated is
        true, only the earliest matches were returned, so narrow the search."""

        if end_time < start_time:
            raise ToolError("end_time must not be before start_time")

        matches = [
            item
            for item in logs
            if start_time <= log_time(item) <= end_time
            and (service is None or item.source_name == service)
            and (correlation_id is None or item.correlation_id == correlation_id)
            and (query is None or matches_query(item, query))
        ]

        matches.sort(key=log_time)
        return LogSearchResult(
            items=matches[:MAX_RESULTS], truncated=len(matches) > MAX_RESULTS
        )

    @server.tool(annotations=ToolAnnotations(read_only_hint=True))
    def search_alerts(
        start_time: AwareDatetime, end_time: AwareDatetime, service: str | None = None
    ) -> AlertResult:
        """List the alerts that fired within a required time range, oldest first.

        Filter by service to see one service's alerts. An empty result means no
        alerts fired in that range.
        """
        if end_time < start_time:
            raise ToolError("end_time must not be before start_time")

        matches = [
            item
            for item in alerts
            if start_time <= fired_at(item) <= end_time
            and (service is None or item.source_name == service)
        ]
        return AlertResult(items=sorted(matches, key=fired_at))

    @server.tool(annotations=ToolAnnotations(read_only_hint=True))
    def get_alert(alert_id: str) -> AlertResult:
        """Get one alert by its ID. An empty result means no alert has that ID."""
        if not alert_id.strip():
            raise ToolError("alert_id must not be blank")

        return AlertResult(
            items=[item for item in alerts if item.evidence_id == alert_id]
        )

    @server.tool(annotations=ToolAnnotations(read_only_hint=True))
    def get_metrics(
        service: str,
        start_time: AwareDatetime,
        end_time: AwareDatetime,
        metric_names: list[str] | None = None,
    ) -> MetricResult:
        """Get a service's metrics within a required time range.

        Each result summarises one metric over the range: its peak, its threshold,
        and when it first went above the threshold, if it did. Without
        metric_names, every metric recorded for the service is returned. An empty
        result means no metrics were recorded for the service in that range.
        """
        if not service.strip():
            raise ToolError("service must not be blank")
        if end_time < start_time:
            raise ToolError("end_time must not be before start_time")

        found = []
        for item in metrics:
            if item.source_name != service:
                continue
            if metric_names is not None and item.metadata["metric"] not in metric_names:
                continue
            summary = within(item, start_time, end_time)
            if summary is not None:
                found.append(summary)
        return MetricResult(items=found)

    return server


server = create_server()


if __name__ == "__main__":
    server.run()
