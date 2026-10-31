# src/flowguard/mcp/servers/observability/server.py
from datetime import datetime

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations
from pydantic import AwareDatetime, BaseModel

from flowguard.dataset import load_evidence
from flowguard.domain.evidence import EvidenceItem

MAX_RESULTS = 50

server = MCPServer("observability-server")
LOGS = [item for item in load_evidence() if item.source_type == "log"]


class LogSearchResult(BaseModel):
    items: list[EvidenceItem]
    truncated: bool


def log_time(item: EvidenceItem) -> datetime:
    if item.timestamp is None:
        raise ValueError(f"{item.evidence_id} has no timestamp")
    return item.timestamp


def matches_query(item: EvidenceItem, query: str) -> bool:
    searchable = f"{item.content} {item.metadata}".lower()
    return query.lower() in searchable


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
        for item in LOGS
        if start_time <= log_time(item) <= end_time
        and (service is None or item.source_name == service)
        and (correlation_id is None or item.correlation_id == correlation_id)
        and (query is None or matches_query(item, query))
    ]

    matches.sort(key=log_time)
    return LogSearchResult(
        items=matches[:MAX_RESULTS], truncated=len(matches) > MAX_RESULTS
    )


if __name__ == "__main__":
    server.run()
