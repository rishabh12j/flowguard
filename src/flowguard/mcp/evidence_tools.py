from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

from mcp import Client
from mcp.shared.exceptions import MCPError
from pydantic import ValidationError

from flowguard.domain.evidence import EvidenceItem
from flowguard.graph.context import EvidenceUnavailable, Found
from flowguard.mcp.clients import GuardedClient
from flowguard.mcp.permissions import ToolDenied, ToolGuard
from flowguard.mcp.servers.knowledge.server import server as knowledge
from flowguard.mcp.servers.observability.server import server as observability
from flowguard.mcp.servers.operations.server import server as operations


class McpEvidenceTools:
    """Gives the graph evidence from the MCP servers, through the tool guard."""

    def __init__(
        self,
        observability: GuardedClient,
        operations: GuardedClient,
        knowledge: GuardedClient,
    ) -> None:
        self._observability = observability
        self._operations = operations
        self._knowledge = knowledge

    async def search_logs(self, start_time: datetime, end_time: datetime) -> Found:
        return await self._call(
            self._observability, "search_logs", window(start_time, end_time)
        )

    async def get_deployments(self, start_time: datetime, end_time: datetime) -> Found:
        return await self._call(
            self._operations, "get_deployments", window(start_time, end_time)
        )

    async def get_dependency_map(self, service: str) -> Found:
        return await self._call(
            self._knowledge, "get_dependency_map", {"service": service}
        )

    async def _call(
        self, client: GuardedClient, name: str, arguments: dict[str, Any]
    ) -> Found:
        try:
            result = await client.call_tool(name, arguments)
        except (ToolDenied, MCPError) as error:
            raise EvidenceUnavailable(f"{name}: {error}") from error

        if result.is_error or result.structured_content is None:
            message = " ".join(getattr(part, "text", "") for part in result.content)
            raise EvidenceUnavailable(f"{name} failed: {message}")

        # The result crossed a process boundary, so it is validated like any input.
        try:
            items = [
                EvidenceItem.model_validate(item)
                for item in result.structured_content["items"]
            ]
        except (KeyError, ValidationError) as error:
            raise EvidenceUnavailable(f"{name} returned malformed evidence") from error
        return Found(items, bool(result.structured_content.get("truncated", False)))


def window(start_time: datetime, end_time: datetime) -> dict[str, Any]:
    return {"start_time": start_time.isoformat(), "end_time": end_time.isoformat()}


@asynccontextmanager
async def open_evidence_tools(
    guard: ToolGuard | None = None,
) -> AsyncIterator[McpEvidenceTools]:
    # One guard is shared by every server, so the investigation has one record of its calls.
    guard = guard or ToolGuard()
    async with (
        Client(observability) as observability_client,
        Client(operations) as operations_client,
        Client(knowledge) as knowledge_client,
    ):
        yield McpEvidenceTools(
            GuardedClient(observability_client, guard),
            GuardedClient(operations_client, guard),
            GuardedClient(knowledge_client, guard),
        )
