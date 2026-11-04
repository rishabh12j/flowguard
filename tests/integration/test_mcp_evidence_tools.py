from datetime import UTC, datetime

import pytest

from flowguard.graph.context import EvidenceUnavailable
from flowguard.mcp.evidence_tools import open_evidence_tools
from flowguard.mcp.permissions import ToolGuard, read_policy

pytestmark = pytest.mark.anyio

START = datetime(2026, 7, 15, 9, tzinfo=UTC)
END = datetime(2026, 7, 15, 11, tzinfo=UTC)


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def test_search_logs_returns_validated_evidence():
    async with open_evidence_tools() as tools:
        found = await tools.search_logs(START, END)

    ids = [item.evidence_id for item in found.items]
    assert ids[0] == "LOG-880"
    assert "LOG-882" in ids
    assert "LOG-860" not in ids
    assert found.truncated is False


async def test_get_deployments_and_dependency_map_return_evidence():
    async with open_evidence_tools() as tools:
        deployments = await tools.get_deployments(
            datetime(2026, 7, 15, 8, tzinfo=UTC), END
        )
        maps = await tools.get_dependency_map("invoice-transformer")

    assert [item.evidence_id for item in deployments.items] == ["DEPLOY-SOURCE-221"]
    assert [item.evidence_id for item in maps.items] == ["DEPMAP-INVOICE"]


async def test_a_tool_error_becomes_evidence_unavailable():
    async with open_evidence_tools() as tools:
        with pytest.raises(EvidenceUnavailable, match="end_time must not be before"):
            await tools.search_logs(END, START)


async def test_the_call_limit_covers_the_whole_investigation():
    guard = ToolGuard({"search_logs": read_policy("search_logs", max_calls=1)})

    async with open_evidence_tools(guard) as tools:
        await tools.search_logs(START, END)
        with pytest.raises(EvidenceUnavailable, match="call limit"):
            await tools.search_logs(START, END)


async def test_a_tool_without_a_policy_is_denied():
    guard = ToolGuard({"search_logs": read_policy("search_logs", max_calls=1)})

    async with open_evidence_tools(guard) as tools:
        with pytest.raises(EvidenceUnavailable, match="not an allowed tool"):
            await tools.get_deployments(START, END)
