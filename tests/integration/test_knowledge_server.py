import sys

import pytest
from mcp import Client

from flowguard.domain.evidence import EvidenceItem
from flowguard.mcp.servers.knowledge import server as module
from flowguard.mcp.servers.knowledge.server import create_server, server

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
    assert all(tool.annotations.read_only_hint is True for tool in tools.tools)


OLD_SPEC = EvidenceItem(
    evidence_id="SPEC-INVOICE-V2",
    source_type="api_spec",
    source_name="invoice-transformer",
    title="Invoice ingestion contract",
    content="A superseded contract.",
    metadata={"version": "2.4", "is_current": False},
)


API_SPECS = [item for item in module.EVIDENCE if item.source_type == "api_spec"]


@pytest.fixture
def with_old_spec(monkeypatch):
    # The tests' server is rebuilt with a superseded spec added to its data.
    monkeypatch.setattr(
        sys.modules[__name__],
        "server",
        create_server(evidence=[OLD_SPEC, *module.EVIDENCE]),
    )


async def api_spec(**arguments):
    async with Client(server) as client:
        return await client.call_tool("get_api_spec", arguments)


async def test_gets_the_current_spec():
    result = await api_spec(service="invoice-transformer")

    assert result.is_error is False
    assert ids(result) == ["SPEC-INVOICE-V3"]
    assert "`supplier_id`" in result.structured_content["items"][0]["content"]


async def test_gets_the_spec_for_the_version_in_a_log():
    assert ids(await api_spec(service="invoice-transformer", version="3.1")) == [
        "SPEC-INVOICE-V3"
    ]


async def test_skips_superseded_specs_by_default(with_old_spec):
    assert ids(await api_spec(service="invoice-transformer")) == ["SPEC-INVOICE-V3"]


async def test_gets_a_superseded_spec_by_version(with_old_spec):
    assert ids(await api_spec(service="invoice-transformer", version="2.4")) == [
        "SPEC-INVOICE-V2"
    ]


async def test_unknown_version_is_empty_not_an_error():
    result = await api_spec(service="invoice-transformer", version="9.9")

    assert result.is_error is False
    assert ids(result) == []


async def test_service_without_a_spec_is_empty_not_an_error():
    result = await api_spec(service="supplier-api")

    assert result.is_error is False
    assert ids(result) == []


async def test_spec_service_must_match_exactly():
    assert ids(await api_spec(service="invoice")) == []


async def test_rejects_a_blank_service_for_a_spec():
    result = await api_spec(service="   ")

    assert result.is_error is True
    assert "service" in result.content[0].text


async def test_rejects_a_blank_version():
    result = await api_spec(service="invoice-transformer", version="   ")

    assert result.is_error is True
    assert "version" in result.content[0].text


class RecordingSearch:
    """Returns one fixed document and records how it was asked."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str, int]] = []

    def __call__(self, query, *, system, limit):
        self.calls.append((query, system, limit))
        return [API_SPECS[0]]


async def search(search_function, **arguments):
    async with Client(create_server(search_function)) as client:
        return await client.call_tool("search_runbooks", arguments)


async def test_search_runbooks_passes_the_query_system_and_limit():
    recording = RecordingSearch()

    result = await search(
        recording, query="schema errors", system="invoice-processing", top_k=3
    )

    assert result.is_error is False
    assert ids(result) == [API_SPECS[0].evidence_id]
    assert recording.calls == [("schema errors", "invoice-processing", 3)]


@pytest.mark.parametrize(
    "arguments, message",
    [
        ({"query": " ", "system": "invoice-processing"}, "query must not be blank"),
        ({"query": "schema", "system": " "}, "system must not be blank"),
        (
            {"query": "schema", "system": "invoice-processing", "top_k": 50},
            "top_k must be between 1 and 10",
        ),
    ],
)
async def test_search_runbooks_refuses_bad_arguments(arguments, message):
    recording = RecordingSearch()

    result = await search(recording, **arguments)

    assert result.is_error is True
    assert message in result.content[0].text
    assert recording.calls == []


async def test_a_server_without_a_search_has_no_search_tool():
    async with Client(server) as client:
        tools = await client.list_tools()

    assert "search_runbooks" not in {tool.name for tool in tools.tools}
