from datetime import UTC, datetime

import pytest
from mcp.types import CallToolResult, TextContent

from flowguard.graph.context import EvidenceUnavailable
from flowguard.mcp.evidence_tools import McpEvidenceTools
from flowguard.mcp.permissions import ToolDenied

pytestmark = pytest.mark.anyio

START = datetime(2026, 7, 15, 9, tzinfo=UTC)
END = datetime(2026, 7, 15, 11, tzinfo=UTC)
LOG = {
    "evidence_id": "LOG-882",
    "source_type": "log",
    "source_name": "invoice-transformer",
    "timestamp": "2026-07-15T09:43:17Z",
    "title": "Payload validation failed",
    "content": "required field supplier_id is missing",
    "metadata": {"level": "ERROR"},
}


@pytest.fixture
def anyio_backend():
    return "asyncio"


class FakeClient:
    """Stands in for a GuardedClient and returns one fixed result."""

    def __init__(self, result: CallToolResult) -> None:
        self.result = result

    async def call_tool(self, name, arguments) -> CallToolResult:
        return self.result


def tools_returning(**result) -> McpEvidenceTools:
    client = FakeClient(
        CallToolResult(content=[TextContent(type="text", text="boom")], **result)
    )
    return McpEvidenceTools(client, client, client)


async def test_an_error_result_is_unavailable_even_with_content():
    tools = tools_returning(
        is_error=True, structured_content={"items": [LOG], "truncated": False}
    )

    with pytest.raises(EvidenceUnavailable, match="boom"):
        await tools.search_logs(START, END)


async def test_the_truncated_flag_is_passed_on():
    tools = tools_returning(structured_content={"items": [LOG], "truncated": True})

    found = await tools.search_logs(START, END)

    assert found.truncated is True
    assert found.items[0].evidence_id == "LOG-882"


@pytest.mark.parametrize(
    "content",
    [{"items": [{**LOG, "evidence_id": "LOG 882"}]}, {"results": [LOG]}],
)
async def test_malformed_evidence_is_unavailable(content):
    tools = tools_returning(structured_content=content)

    with pytest.raises(EvidenceUnavailable, match="malformed"):
        await tools.search_logs(START, END)


async def test_a_successful_call_is_recorded():
    tools = tools_returning(structured_content={"items": [LOG], "truncated": True})

    await tools.search_logs(START, END)

    [call] = tools.history
    assert call.tool == "search_logs"
    assert call.arguments == {
        "start_time": START.isoformat(),
        "end_time": END.isoformat(),
    }
    assert (call.outcome, call.items, call.truncated) == ("ok", 1, True)


async def test_a_failed_call_is_recorded():
    tools = tools_returning(is_error=True)

    with pytest.raises(EvidenceUnavailable):
        await tools.search_logs(START, END)

    [call] = tools.history
    assert (call.outcome, call.detail) == ("failed", "boom")


class DenyingClient:
    async def call_tool(self, name, arguments):
        raise ToolDenied(f"{name} has reached its call limit")


async def test_a_denied_call_is_recorded():
    client = DenyingClient()
    tools = McpEvidenceTools(client, client, client)

    with pytest.raises(EvidenceUnavailable):
        await tools.get_dependency_map("invoice-transformer")

    [call] = tools.history
    assert call.outcome == "denied"
    assert call.detail == "get_dependency_map has reached its call limit"
