# tests/integration/test_observability_server.py
import pytest
from mcp import Client

from flowguard.mcp.servers.observability import server as module
from flowguard.mcp.servers.observability.server import server

pytestmark = pytest.mark.anyio

WINDOW = {
    "start_time": "2026-07-15T09:00:00Z",
    "end_time": "2026-07-15T11:00:00Z",
}


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def test_traces_a_transaction_across_services():
    async with Client(server) as client:
        result = await client.call_tool(
            "search_logs", {**WINDOW, "correlation_id": "CORR-2048"}
        )

    assert result.is_error is False
    ids = [item["evidence_id"] for item in result.structured_content["items"]]
    assert ids == ["LOG-880", "LOG-881", "LOG-882", "LOG-883"]


async def test_finds_an_invoice_by_its_id():
    assert ids(await search(**WINDOW, query="inv-2048")) == ["LOG-880"]


async def test_stays_inside_the_time_window():
    assert "LOG-861" not in ids(await search(**WINDOW))


async def test_rejects_a_timestamp_without_a_timezone():
    result = await search(
        start_time="2026-07-15T09:00:00", end_time="2026-07-15T11:00:00"
    )

    assert result.is_error is True


async def test_tool_is_marked_read_only():
    async with Client(server) as client:
        tools = await client.list_tools()

    assert tools.tools[0].annotations.read_only_hint is True


async def search(**arguments):
    async with Client(server) as client:
        return await client.call_tool("search_logs", arguments)


def ids(result):
    return [item["evidence_id"] for item in result.structured_content["items"]]


async def test_no_match_is_empty_not_an_error():
    result = await search(
        **WINDOW, service="invoice-workflow", correlation_id="CORR-2048"
    )

    assert result.is_error is False
    assert ids(result) == []


async def test_truncation_keeps_the_earliest_logs(monkeypatch):
    monkeypatch.setattr(module, "MAX_RESULTS", 2)

    result = await search(**WINDOW)

    assert result.structured_content["truncated"] is True
    assert ids(result) == ["LOG-880", "LOG-881"]


async def test_exact_limit_is_not_truncated(monkeypatch):
    monkeypatch.setattr(module, "MAX_RESULTS", 4)

    result = await search(**WINDOW, correlation_id="CORR-2048")

    assert result.structured_content["truncated"] is False
    assert len(ids(result)) == 4


async def test_rejects_a_reversed_time_window():
    result = await search(start_time=WINDOW["end_time"], end_time=WINDOW["start_time"])

    assert result.is_error is True
