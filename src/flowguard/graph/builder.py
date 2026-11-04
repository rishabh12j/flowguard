from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command

from flowguard.domain.approval import ApprovalDecision
from flowguard.domain.redaction import redact_value
from flowguard.graph.context import Dependencies
from flowguard.graph.nodes.approval import approval
from flowguard.graph.nodes.audit import audit
from flowguard.graph.nodes.dependency_trace import dependency_trace
from flowguard.graph.nodes.intake import intake
from flowguard.graph.nodes.log_analysis import log_analysis
from flowguard.graph.nodes.remediation import remediation
from flowguard.graph.nodes.retrieval import runbook_retrieval
from flowguard.graph.nodes.root_cause import root_cause
from flowguard.graph.nodes.validation import validation
from flowguard.graph.routing import after_audit, after_intake, after_root_cause
from flowguard.graph.state import InvestigationState

InvestigationGraph = CompiledStateGraph[
    InvestigationState, Dependencies, InvestigationState, InvestigationState
]


# The checkpointer is required: without one, the graph couldn't pause for approval.
def build_graph(checkpointer: BaseCheckpointSaver[Any]) -> InvestigationGraph:
    graph = StateGraph(InvestigationState, context_schema=Dependencies)
    graph.add_node("intake", intake)
    graph.add_node("log_analysis", log_analysis)
    graph.add_node("dependency_trace", dependency_trace)
    graph.add_node("runbook_retrieval", runbook_retrieval)
    graph.add_node("root_cause", root_cause)
    graph.add_node("remediation", remediation)
    graph.add_node("validation", validation)
    graph.add_node("audit", audit)
    graph.add_node("approval", approval)

    graph.add_edge(START, "intake")
    graph.add_conditional_edges(
        "intake", after_intake, ["log_analysis", "runbook_retrieval", "audit"]
    )
    # Dependency tracing starts from the first failure, so it waits for log analysis.
    graph.add_edge("log_analysis", "dependency_trace")
    # Root cause waits for both branches, so it reasons over all the evidence.
    graph.add_edge(["dependency_trace", "runbook_retrieval"], "root_cause")
    graph.add_conditional_edges(
        "root_cause", after_root_cause, ["remediation", "audit"]
    )
    graph.add_edge("remediation", "validation")
    graph.add_edge("validation", "audit")
    # A plan that needs approval is saved, waits for a decision, and is saved again.
    graph.add_conditional_edges("audit", after_audit, ["approval", END])
    graph.add_edge("approval", "audit")

    return graph.compile(checkpointer=checkpointer)


def new_investigation_id() -> str:
    return f"INVEST-{uuid4().hex[:12]}"


async def investigate(
    graph: InvestigationGraph,
    request: dict[str, Any],
    dependencies: Dependencies,
    *,
    investigation_id: str | None = None,
) -> dict[str, Any]:
    investigation_id = investigation_id or new_investigation_id()
    return await graph.ainvoke(
        {
            "investigation_id": investigation_id,
            "started_at": datetime.now(UTC),
            # Redacted before it enters the graph: the checkpointer saves the input
            # before any node runs, and keeps every checkpoint after that.
            "request": redact_value("", request),
        },
        # The checkpointer keeps each investigation's state under its own ID.
        {"configurable": {"thread_id": investigation_id}},
        context=dependencies,
    )


async def decide(
    graph: InvestigationGraph,
    investigation_id: str,
    decision: ApprovalDecision,
    dependencies: Dependencies,
) -> dict[str, Any]:
    # Resumes the paused approval node, which receives the decision.
    return await graph.ainvoke(
        Command(resume=decision),
        {"configurable": {"thread_id": investigation_id}},
        context=dependencies,
    )
