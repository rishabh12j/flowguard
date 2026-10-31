import pytest
from mcp import Client

from flowguard.mcp.servers.operations import server as module
from flowguard.mcp.servers.operations.server import server

pytestmark = pytest.mark.anyio

LOOKBACK = {
    "start_time": "2026-07-14T09:43:17Z",
    "end_time": "2026-07-15T09:43:17Z",
}
INCIDENT_WINDOW = {
    "start_time": "2026-07-15T09:00:00Z",
    "end_time": "2026-07-15T11:00:00Z",
}


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def deployments(**arguments):
    async with Client(server) as client:
        return await client.call_tool("get_deployments", arguments)


def ids(result):
    return [item["evidence_id"] for item in result.structured_content["items"]]


async def test_lists_recent_deployments_newest_first():
    result = await deployments(**LOOKBACK)

    assert result.is_error is False
    assert ids(result) == ["DEPLOY-SOURCE-221", "DEPLOY-WORKFLOW-118"]


async def test_filters_by_service():
    result = await deployments(**LOOKBACK, service="supplier-api")

    assert ids(result) == ["DEPLOY-SOURCE-221"]


async def test_incident_window_misses_the_deployment():
    assert ids(await deployments(**INCIDENT_WINDOW)) == []


async def test_excludes_deployments_after_the_range():
    result = await deployments(
        start_time="2026-07-14T00:00:00Z", end_time="2026-07-15T00:00:00Z"
    )

    assert ids(result) == ["DEPLOY-WORKFLOW-118"]


async def test_no_deployment_is_empty_not_an_error():
    result = await deployments(**LOOKBACK, service="invoice-transformer")

    assert result.is_error is False
    assert ids(result) == []


async def test_truncation_keeps_the_newest_deployments(monkeypatch):
    monkeypatch.setattr(module, "MAX_RESULTS", 1)

    result = await deployments(**LOOKBACK)

    assert result.structured_content["truncated"] is True
    assert ids(result) == ["DEPLOY-SOURCE-221"]


async def test_exact_limit_is_not_truncated(monkeypatch):
    monkeypatch.setattr(module, "MAX_RESULTS", 2)

    result = await deployments(**LOOKBACK)

    assert result.structured_content["truncated"] is False


async def test_rejects_a_timestamp_without_a_timezone():
    result = await deployments(
        start_time="2026-07-14T09:43:17", end_time="2026-07-15T09:43:17"
    )

    assert result.is_error is True
    assert "timezone" in result.content[0].text


async def test_rejects_a_reversed_time_window():
    result = await deployments(
        start_time=LOOKBACK["end_time"], end_time=LOOKBACK["start_time"]
    )

    assert result.is_error is True
    assert "end_time" in result.content[0].text


async def test_tool_is_marked_read_only():
    async with Client(server) as client:
        tools = await client.list_tools()

    assert tools.tools[0].annotations.read_only_hint is True
