from typing import Protocol

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations
from pydantic import BaseModel

from flowguard.dataset import load_evidence
from flowguard.domain.evidence import EvidenceItem

MAX_TOP_K = 10

EVIDENCE = load_evidence()
DEPENDENCY_MAPS = [item for item in EVIDENCE if item.source_type == "dependency_map"]
API_SPECS = [item for item in EVIDENCE if item.source_type == "api_spec"]


class DocumentSearch(Protocol):
    def __call__(
        self, query: str, *, system: str, limit: int, document_type: str | None = None
    ) -> list[EvidenceItem]: ...


class DependencyMapResult(BaseModel):
    items: list[EvidenceItem]


class ApiSpecResult(BaseModel):
    items: list[EvidenceItem]


class DocumentSearchResult(BaseModel):
    items: list[EvidenceItem]


def contains_node(item: EvidenceItem, name: str) -> bool:
    return any(node["name"] == name for node in item.metadata["nodes"])


def is_requested_version(item: EvidenceItem, version: str | None) -> bool:
    if version is None:
        return item.metadata["is_current"]
    return item.metadata["version"] == version


def create_server(search: DocumentSearch | None = None) -> MCPServer:
    """The knowledge server. Without a search, it has no search_runbooks tool."""
    server = MCPServer("knowledge-server")

    @server.tool(annotations=ToolAnnotations(read_only_hint=True))
    def get_dependency_map(service: str) -> DependencyMapResult:
        """Get the dependency maps that include a service, queue, or database.

        The name must match exactly. Each map lists its nodes and the edges between
        them, so you can work out what sits upstream and downstream. An empty result
        means the name is in no map, so it may be an undocumented dependency.
        """
        if not service.strip():
            raise ToolError("service must not be blank")

        return DependencyMapResult(
            items=[item for item in DEPENDENCY_MAPS if contains_node(item, service)]
        )

    @server.tool(annotations=ToolAnnotations(read_only_hint=True))
    def get_api_spec(service: str, version: str | None = None) -> ApiSpecResult:
        """Get the API contract a service validates against.

        The service name must match exactly. Without a version, only the current
        contract is returned. Pass a version, such as the schema_version in a log,
        to see the contract in force at that time, even if it has been superseded.
        An empty result means no contract is on file for that service and version.
        """
        if not service.strip():
            raise ToolError("service must not be blank")
        if version is not None and not version.strip():
            raise ToolError("version must not be blank")

        return ApiSpecResult(
            items=[
                item
                for item in API_SPECS
                if item.source_name == service and is_requested_version(item, version)
            ]
        )

    if search is not None:

        @server.tool(annotations=ToolAnnotations(read_only_hint=True))
        def search_runbooks(
            query: str, system: str, top_k: int = 5
        ) -> DocumentSearchResult:
            """Search current runbooks, API specifications, and past incidents.

            Only documents for the given system are searched, and superseded
            documents are never returned. Results are the closest matches above a
            relevance threshold, best first, so an empty result means nothing
            relevant was found. top_k must be between 1 and 10.
            """
            if not query.strip():
                raise ToolError("query must not be blank")
            if not system.strip():
                raise ToolError("system must not be blank")
            if not 1 <= top_k <= MAX_TOP_K:
                raise ToolError(f"top_k must be between 1 and {MAX_TOP_K}")

            return DocumentSearchResult(items=search(query, system=system, limit=top_k))

    return server


# The dependency-map and API-spec tools, for clients that don't search documents.
server = create_server()


if __name__ == "__main__":
    from functools import partial

    from qdrant_client import QdrantClient

    from flowguard.rag.embedding import SentenceTransformerEmbedder
    from flowguard.rag.ingestion import ingest, knowledge_chunks
    from flowguard.rag.retrieval import retrieve

    embedder = SentenceTransformerEmbedder()
    client = QdrantClient(":memory:")
    ingest(knowledge_chunks(EVIDENCE), embedder, client)
    create_server(partial(retrieve, embedder=embedder, client=client)).run()
