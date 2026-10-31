from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations
from pydantic import BaseModel

from flowguard.dataset import load_evidence
from flowguard.domain.evidence import EvidenceItem

server = MCPServer("knowledge-server")
DEPENDENCY_MAPS = [
    item for item in load_evidence() if item.source_type == "dependency_map"
]


class DependencyMapResult(BaseModel):
    items: list[EvidenceItem]


def contains_node(item: EvidenceItem, name: str) -> bool:
    return any(node["name"] == name for node in item.metadata["nodes"])


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


if __name__ == "__main__":
    server.run()
