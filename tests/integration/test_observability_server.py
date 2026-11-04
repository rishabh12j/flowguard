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
    assert "timezone" in result.content[0].text


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
    assert "end_time" in result.content[0].text


async def test_finds_failures_by_exception_type():
    result = await search(**WINDOW, query="SchemaValidationError")

    assert ids(result) == ["LOG-882", "LOG-886", "LOG-890"]


INC_002_DAY = {
    "start_time": "2026-08-02T06:00:00Z",
    "end_time": "2026-08-03T06:00:04Z",
}


async def call(name, arguments):
    async with Client(server) as client:
        return await client.call_tool(name, arguments)


def found(result):
    return [item["evidence_id"] for item in result.structured_content["items"]]


async def test_alerts_in_a_range_come_oldest_first():
    result = await call("search_alerts", INC_002_DAY)

    assert found(result) == ["ALERT-309", "ALERT-311"]


async def test_alerts_can_be_filtered_by_service():
    result = await call(
        "search_alerts", {**INC_002_DAY, "service": "settlement-importer"}
    )

    assert found(result) == ["ALERT-311"]


async def test_one_alert_by_id():
    assert found(await call("get_alert", {"alert_id": "ALERT-311"})) == ["ALERT-311"]
    assert found(await call("get_alert", {"alert_id": "ALERT-999"})) == []


async def test_metrics_are_summarised_over_the_range_asked_for():
    result = await call(
        "get_metrics",
        {
            "service": "order-sync-worker",
            "start_time": "2026-08-09T14:02:10Z",
            "end_time": "2026-08-10T14:02:10Z",
        },
    )

    [metric] = result.structured_content["items"]
    assert metric["evidence_id"] == "METRIC-ORDERSYNC-OUTBOUND"
    # The spike's first point at or above the threshold, before the first 429.
    assert metric["timestamp"] == "2026-08-10T14:00:00Z"
    assert metric["metadata"]["threshold"] == 100


async def test_metrics_can_be_chosen_by_name():
    result = await call(
        "get_metrics",
        {
            "service": "storefront",
            "metric_names": ["orders_per_minute"],
            "start_time": "2026-08-10T12:00:00Z",
            "end_time": "2026-08-10T15:00:00Z",
        },
    )
    none = await call(
        "get_metrics",
        {
            "service": "storefront",
            "metric_names": ["error_rate"],
            "start_time": "2026-08-10T12:00:00Z",
            "end_time": "2026-08-10T15:00:00Z",
        },
    )

    assert found(result) == ["METRIC-STOREFRONT-ORDERS"]
    assert found(none) == []


@pytest.mark.parametrize("tool", ["search_alerts", "get_metrics"])
async def test_a_backwards_range_is_refused(tool):
    arguments = {
        "start_time": "2026-08-10T15:00:00Z",
        "end_time": "2026-08-10T12:00:00Z",
    }
    if tool == "get_metrics":
        arguments["service"] = "storefront"

    result = await call(tool, arguments)

    assert result.is_error is True
    assert "end_time must not be before start_time" in result.content[0].text


async def test_a_range_before_the_spike_shows_no_crossing():
    result = await call(
        "get_metrics",
        {
            "service": "order-sync-worker",
            "start_time": "2026-08-10T12:00:00Z",
            "end_time": "2026-08-10T13:55:00Z",
        },
    )

    [metric] = result.structured_content["items"]
    assert metric["timestamp"] is None
    # 12:00 to 13:50, every 10 minutes.
    assert len(metric["metadata"]["points"]) == 12
