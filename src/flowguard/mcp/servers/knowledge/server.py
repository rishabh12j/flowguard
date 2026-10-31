from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations
from pydantic import BaseModel

from flowguard.dataset import load_evidence
from flowguard.domain.evidence import EvidenceItem

server = MCPServer("knowledge-server")

EVIDENCE = load_evidence()
DEPENDENCY_MAPS = [item for item in EVIDENCE if item.source_type == "dependency_map"]
API_SPECS = [item for item in EVIDENCE if item.source_type == "api_spec"]


class DependencyMapResult(BaseModel):
    items: list[EvidenceItem]


class ApiSpecResult(BaseModel):
    items: list[EvidenceItem]


def contains_node(item: EvidenceItem, name: str) -> bool:
    return any(node["name"] == name for node in item.metadata["nodes"])


def is_requested_version(item: EvidenceItem, version: str | None) -> bool:
    if version is None:
        return item.metadata["is_current"]
    return item.metadata["version"] == version


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


if __name__ == "__main__":
    server.run()
