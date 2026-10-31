# src/flowguard/mcp/servers/operations/server.py
from datetime import datetime

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations
from pydantic import AwareDatetime, BaseModel

from flowguard.dataset import load_evidence
from flowguard.domain.evidence import EvidenceItem

MAX_RESULTS = 20

server = MCPServer("operations-server")
DEPLOYMENTS = [item for item in load_evidence() if item.source_type == "deployment"]


class DeploymentSearchResult(BaseModel):
    items: list[EvidenceItem]
    truncated: bool


def deployed_at(item: EvidenceItem) -> datetime:
    if item.timestamp is None:
        raise ValueError(f"{item.evidence_id} has no timestamp")
    return item.timestamp


@server.tool(annotations=ToolAnnotations(read_only_hint=True))
def get_deployments(
    start_time: AwareDatetime,
    end_time: AwareDatetime,
    service: str | None = None,
) -> DeploymentSearchResult:
    """List deployments within a required time range, newest first.

    A deployment can cause failures long after it finishes, so start the range
    well before the first failure, not at the incident window. Leave service
    empty to see every deployment, which helps when a dependency is undocumented.
    An empty result means nothing was deployed. If truncated is true, only the
    newest matches were returned, so narrow the search.
    """
    if end_time < start_time:
        raise ToolError("end_time must not be before start_time")

    matches = [
        item
        for item in DEPLOYMENTS
        if start_time <= deployed_at(item) <= end_time
        and (service is None or item.source_name == service)
    ]
    matches.sort(key=deployed_at, reverse=True)
    return DeploymentSearchResult(
        items=matches[:MAX_RESULTS], truncated=len(matches) > MAX_RESULTS
    )


if __name__ == "__main__":
    server.run()
