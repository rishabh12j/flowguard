from typing import Any

from mcp import Client
from mcp.types import CallToolResult

from flowguard.mcp.permissions import ToolDenied, ToolGuard


class GuardedClient:
    """The only way the investigation should reach an MCP server."""

    def __init__(self, client: Client, guard: ToolGuard) -> None:
        self._client = client
        self._guard = guard

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> CallToolResult:
        listed = await self._client.list_tools()
        schemas = {tool.name: tool.input_schema for tool in listed.tools}
        if name not in schemas:
            raise ToolDenied(f"{name} is not available on this server")

        allowed_arguments = set(schemas[name].get("properties", {}))
        policy = self._guard.authorise(name, arguments, allowed_arguments)
        return await self._client.call_tool(
            name, arguments, read_timeout_seconds=policy.timeout_seconds
        )
