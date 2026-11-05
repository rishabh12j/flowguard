from collections.abc import Sequence
from datetime import datetime

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations
from pydantic import AwareDatetime, BaseModel

from flowguard.dataset import load_evidence
from flowguard.domain.evidence import EvidenceItem
from flowguard.mcp.servers.knowledge.server import MAX_TOP_K, DocumentSearch

MAX_RESULTS = 20

# The seeded data, used when a server isn't given its own.
EVIDENCE = load_evidence()


class DeploymentSearchResult(BaseModel):
    items: list[EvidenceItem]
    truncated: bool


class IncidentResult(BaseModel):
    items: list[EvidenceItem]


def deployed_at(item: EvidenceItem) -> datetime:
    if item.timestamp is None:
        raise ValueError(f"{item.evidence_id} has no timestamp")
    return item.timestamp


def create_server(
    search: DocumentSearch | None = None,
    evidence: Sequence[EvidenceItem] | None = None,
) -> MCPServer:
    """The operations server. Without a search, it has no search_incidents tool."""
    source = EVIDENCE if evidence is None else evidence
    deployments = [item for item in source if item.source_type == "deployment"]
    past_incidents = [
        item for item in source if item.source_type == "historical_incident"
    ]
    server = MCPServer("operations-server")

    @server.tool(annotations=ToolAnnotations(read_only_hint=True))
    def get_deployments(
        start_time: AwareDatetime,
        end_time: AwareDatetime,
        service: str | None = None,
    ) -> DeploymentSearchResult:
        """List deployments within a required time range, newest first.

        A deployment can cause failures long after it finishes, so start the range
        well before the first failure, not at the incident window. Leave service
        empty to see every deployment, which helps when a dependency is
        undocumented. An empty result means nothing was deployed. If truncated is
        true, only the newest matches were returned, so narrow the search.
        """
        if end_time < start_time:
            raise ToolError("end_time must not be before start_time")

        matches = [
            item
            for item in deployments
            if start_time <= deployed_at(item) <= end_time
            and (service is None or item.source_name == service)
        ]
        matches.sort(key=deployed_at, reverse=True)
        return DeploymentSearchResult(
            items=matches[:MAX_RESULTS], truncated=len(matches) > MAX_RESULTS
        )

    @server.tool(annotations=ToolAnnotations(read_only_hint=True))
    def get_incident(incident_id: str) -> IncidentResult:
        """Get the full record of a past incident, such as HIST-INC-044.

        An empty result means no past incident has that ID.
        """
        if not incident_id.strip():
            raise ToolError("incident_id must not be blank")

        return IncidentResult(
            items=[item for item in past_incidents if item.evidence_id == incident_id]
        )

    if search is not None:

        @server.tool(annotations=ToolAnnotations(read_only_hint=True))
        def search_incidents(query: str, system: str, top_k: int = 3) -> IncidentResult:
            """Search past incidents in one system for ones like the current one.

            Results are the closest matches above a relevance threshold, best
            first, so an empty result means no similar incident is on record.
            top_k must be between 1 and 10.
            """
            if not query.strip():
                raise ToolError("query must not be blank")
            if not system.strip():
                raise ToolError("system must not be blank")
            if not 1 <= top_k <= MAX_TOP_K:
                raise ToolError(f"top_k must be between 1 and {MAX_TOP_K}")

            # The type is part of the search, so other documents can't fill the limit.
            return IncidentResult(
                items=search(
                    query,
                    system=system,
                    limit=top_k,
                    document_type="historical_incident",
                )
            )

    return server


# The tools that need no document search, for clients that don't search.
server = create_server()


if __name__ == "__main__":
    server.run()
