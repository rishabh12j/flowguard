import pytest
from mcp import Client

from flowguard.mcp.servers.knowledge.server import server

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def dependency_map(**arguments):
    async with Client(server) as client:
        return await client.call_tool("get_dependency_map", arguments)


def ids(result):
    return [item["evidence_id"] for item in result.structured_content["items"]]


async def test_finds_the_map_for_a_service():
    result = await dependency_map(service="invoice-transformer")

    assert result.is_error is False
    assert ids(result) == ["DEPMAP-INVOICE"]


async def test_finds_the_map_for_a_queue():
    assert ids(await dependency_map(service="invoice-transform-dlq")) == [
        "DEPMAP-INVOICE"
    ]


async def test_returns_the_edges_needed_to_trace_the_path():
    result = await dependency_map(service="invoice-transformer")

    edges = result.structured_content["items"][0]["metadata"]["edges"]
    assert {"from": "supplier-api", "to": "invoice-transformer"} in edges
    assert {"from": "invoice-transformer", "to": "invoice-workflow"} in edges


async def test_unmapped_service_is_empty_not_an_error():
    result = await dependency_map(service="shadow-billing-api")

    assert result.is_error is False
    assert ids(result) == []


async def test_name_must_match_exactly():
    assert ids(await dependency_map(service="invoice")) == []
    assert ids(await dependency_map(service="INVOICE-TRANSFORMER")) == []


async def test_rejects_a_blank_service():
    result = await dependency_map(service="   ")

    assert result.is_error is True
    assert "service" in result.content[0].text


async def test_tool_is_marked_read_only():
    async with Client(server) as client:
        tools = await client.list_tools()

    assert tools.tools[0].annotations.read_only_hint is True
