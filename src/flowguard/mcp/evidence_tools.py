import time
from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

from mcp import Client
from mcp.shared.exceptions import MCPError
from pydantic import ValidationError

from flowguard.domain.audit import ToolCallRecord, ToolOutcome
from flowguard.domain.evidence import EvidenceItem
from flowguard.domain.redaction import redact_evidence
from flowguard.graph.context import EvidenceUnavailable, Found
from flowguard.mcp.clients import GuardedClient
from flowguard.mcp.permissions import ToolDenied, ToolGuard
from flowguard.mcp.servers.knowledge.server import DocumentSearch
from flowguard.mcp.servers.knowledge.server import create_server as knowledge_server
from flowguard.mcp.servers.observability.server import (
    create_server as observability_server,
)
from flowguard.mcp.servers.operations.server import create_server as operations_server


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
        self.history: list[ToolCallRecord] = []

    async def search_logs(self, start_time: datetime, end_time: datetime) -> Found:
        return await self._call(
            self._observability, "search_logs", window(start_time, end_time)
        )

    async def search_alerts(self, start_time: datetime, end_time: datetime) -> Found:
        return await self._call(
            self._observability, "search_alerts", window(start_time, end_time)
        )

    async def get_metrics(
        self, service: str, start_time: datetime, end_time: datetime
    ) -> Found:
        return await self._call(
            self._observability,
            "get_metrics",
            {"service": service, **window(start_time, end_time)},
        )

    async def get_deployments(self, start_time: datetime, end_time: datetime) -> Found:
        return await self._call(
            self._operations, "get_deployments", window(start_time, end_time)
        )

    async def get_dependency_map(self, service: str) -> Found:
        return await self._call(
            self._knowledge, "get_dependency_map", {"service": service}
        )

    async def search_runbooks(self, query: str, system: str) -> Found:
        return await self._call(
            self._knowledge, "search_runbooks", {"query": query, "system": system}
        )

    async def _call(
        self, client: GuardedClient, name: str, arguments: dict[str, Any]
    ) -> Found:
        started = time.perf_counter()

        def record(
            outcome: ToolOutcome, detail: str = "", found: Found | None = None
        ) -> None:
            self.history.append(
                ToolCallRecord(
                    tool=name,
                    arguments=arguments,
                    outcome=outcome,
                    detail=detail,
                    items=len(found.items) if found else 0,
                    truncated=found.truncated if found else False,
                    seconds=round(time.perf_counter() - started, 3),
                )
            )

        try:
            result = await client.call_tool(name, arguments)
        except ToolDenied as error:
            record("denied", str(error))
            raise EvidenceUnavailable(f"{name}: {error}") from error
        except MCPError as error:
            record("failed", str(error))
            raise EvidenceUnavailable(f"{name}: {error}") from error

        if result.is_error or result.structured_content is None:
            message = " ".join(getattr(part, "text", "") for part in result.content)
            record("failed", message)
            raise EvidenceUnavailable(f"{name} failed: {message}")

        # The result crossed a process boundary, so it is validated like any input,
        # and credentials are removed before anything else can see them.
        try:
            items = [
                redact_evidence(EvidenceItem.model_validate(item))
                for item in result.structured_content["items"]
            ]
        except (KeyError, ValidationError) as error:
            record("failed", "malformed evidence")
            raise EvidenceUnavailable(f"{name} returned malformed evidence") from error
        found = Found(items, bool(result.structured_content.get("truncated", False)))
        record("ok", found=found)
        return found


def window(start_time: datetime, end_time: datetime) -> dict[str, Any]:
    return {"start_time": start_time.isoformat(), "end_time": end_time.isoformat()}


@asynccontextmanager
async def open_evidence_tools(
    search: DocumentSearch,
    guard: ToolGuard | None = None,
    *,
    evidence: Sequence[EvidenceItem] | None = None,
) -> AsyncIterator[McpEvidenceTools]:
    # The search is required, so the investigation can't be wired up without a way
    # to find documents. It's shared, because loading the embedder is slow.
    # One guard is shared by every server, so the investigation has one record of its calls.
    guard = guard or ToolGuard()
    async with (
        # Without evidence, the servers serve the seeded data.
        Client(observability_server(evidence)) as observability_client,
        Client(operations_server(search, evidence)) as operations_client,
        Client(knowledge_server(search, evidence)) as knowledge_client,
    ):
        yield McpEvidenceTools(
            GuardedClient(observability_client, guard),
            GuardedClient(operations_client, guard),
            GuardedClient(knowledge_client, guard),
        )
