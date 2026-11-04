from datetime import UTC, datetime

import pytest
from mcp.types import CallToolResult, TextContent

from flowguard.graph.context import EvidenceUnavailable
from flowguard.mcp.evidence_tools import McpEvidenceTools

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
