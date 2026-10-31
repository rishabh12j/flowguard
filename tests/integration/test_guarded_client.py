import anyio
import pytest
from mcp import Client
from mcp.server import MCPServer
from mcp.shared.exceptions import MCPError

from flowguard.mcp.clients import GuardedClient
from flowguard.mcp.permissions import POLICIES, ToolDenied, ToolGuard, read_policy
from flowguard.mcp.servers.knowledge.server import server as knowledge
from flowguard.mcp.servers.observability.server import server as observability
from flowguard.mcp.servers.operations.server import server as operations

pytestmark = pytest.mark.anyio

WINDOW = {
    "start_time": "2026-07-15T09:00:00Z",
    "end_time": "2026-07-15T11:00:00Z",
}

demo = MCPServer("demo")
tool_ran = []


@demo.tool()
def delete_everything() -> str:
    tool_ran.append("delete_everything")
    return "deleted"


# The in-memory client only times out async tools. Real subprocesses time out both.
@demo.tool()
async def slow_tool() -> str:
    await anyio.sleep(1)
    return "finished"


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def test_an_allowed_call_reaches_the_server():
    async with Client(observability) as client:
        guarded = GuardedClient(client, ToolGuard())
        result = await guarded.call_tool(
            "search_logs", {**WINDOW, "correlation_id": "CORR-2048"}
        )

    assert result.is_error is False
    assert len(result.structured_content["items"]) == 4


async def test_blocks_a_tool_without_a_policy_before_it_runs():
    tool_ran.clear()

    async with Client(demo) as client:
        with pytest.raises(ToolDenied, match="not an allowed tool"):
            await GuardedClient(client, ToolGuard()).call_tool("delete_everything", {})

    assert tool_ran == []


async def test_blocks_an_unknown_argument():
    async with Client(observability) as client:
        with pytest.raises(ToolDenied, match="shell"):
            await GuardedClient(client, ToolGuard()).call_tool(
                "search_logs", {**WINDOW, "shell": "rm -rf"}
            )


async def test_blocks_a_tool_this_server_does_not_have():
    async with Client(observability) as client:
        with pytest.raises(ToolDenied, match="not available"):
            await GuardedClient(client, ToolGuard()).call_tool("get_api_spec", {})


async def test_blocks_calls_over_the_limit():
    guard = ToolGuard({"search_logs": read_policy("search_logs", max_calls=1)})

    async with Client(observability) as client:
        guarded = GuardedClient(client, guard)
        await guarded.call_tool("search_logs", WINDOW)

        with pytest.raises(ToolDenied, match="call limit"):
            await guarded.call_tool("search_logs", WINDOW)


async def test_a_limit_is_shared_across_connections():
    guard = ToolGuard({"search_logs": read_policy("search_logs", max_calls=1)})

    async with Client(observability) as first:
        await GuardedClient(first, guard).call_tool("search_logs", WINDOW)

    async with Client(observability) as second:
        with pytest.raises(ToolDenied, match="call limit"):
            await GuardedClient(second, guard).call_tool("search_logs", WINDOW)


async def test_a_slow_tool_times_out():
    policy = read_policy("slow_tool", max_calls=1).model_copy(
        update={"timeout_seconds": 0.05}
    )

    async with Client(demo) as client:
        with pytest.raises(MCPError, match="Timed out"):
            await GuardedClient(client, ToolGuard({"slow_tool": policy})).call_tool(
                "slow_tool", {}
            )


async def test_every_server_tool_has_a_policy():
    names = set()
    for server in (observability, operations, knowledge):
        async with Client(server) as client:
            listed = await client.list_tools()
        names |= {tool.name for tool in listed.tools}

    assert names == set(POLICIES)
