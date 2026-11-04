from datetime import UTC, datetime, timedelta

import pytest
from fakes import FakeLLM
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.errors import GraphRecursionError
from langgraph.runtime import Runtime
from langgraph.types import Command
from pydantic import ValidationError

from flowguard.domain.approval import ApprovalDecision
from flowguard.domain.audit import ToolCallRecord
from flowguard.domain.evidence import EvidenceItem
from flowguard.domain.incidents import Incident
from flowguard.graph.builder import build_graph, decide, investigate
from flowguard.graph.checkpoints import SERIALIZER, open_checkpointer
from flowguard.graph.context import Dependencies, EvidenceUnavailable, Found
from flowguard.graph.nodes.root_cause import root_cause
from flowguard.llm.client import LLMError

pytestmark = pytest.mark.anyio

REQUEST = {
    "incident_id": "INC-001",
    "description": "Invoice INV-2048 did not enter the approval workflow.",
    "affected_system": "invoice-processing",
    "start_time": "2026-07-15T09:00:00Z",
    "end_time": "2026-07-15T11:00:00Z",
}
WINDOW_START = datetime(2026, 7, 15, 9, tzinfo=UTC)


@pytest.fixture
def anyio_backend():
    return "asyncio"


def document(evidence_id: str, source_type: str = "runbook") -> EvidenceItem:
    return EvidenceItem(
        evidence_id=evidence_id,
        source_type=source_type,
        source_name="invoice-transformer",
        title="A runbook",
        content="Some steps.",
        metadata={},
        retrieval_score=0.7,
    )


def log(evidence_id: str, minute: int, level: str, service: str) -> EvidenceItem:
    return EvidenceItem(
        evidence_id=evidence_id,
        source_type="log",
        source_name=service,
        timestamp=WINDOW_START + timedelta(minutes=minute),
        title=f"{level} from {service}",
        content="A log message.",
        metadata={"level": level},
    )


def deployment(evidence_id: str, at: datetime, service: str) -> EvidenceItem:
    return EvidenceItem(
        evidence_id=evidence_id,
        source_type="deployment",
        source_name=service,
        timestamp=at,
        title=f"{service} deployment",
        content="Deployed.",
        metadata={},
    )


def step(action: str, target: str, *evidence_ids: str) -> dict:
    return {
        "action": action,
        "target": target,
        "reason": "The mapping still expects snake_case fields.",
        "evidence_ids": list(evidence_ids or ("LOG-882",)),
    }


INC_001_PLAN = [
    step("update_field_mapping", "invoice-transformer"),
    step("replay_failed_messages", "invoice-transformer"),
    step("add_contract_test", "supplier-api", "DEPLOY-SOURCE-221"),
]


def proposal(
    *supporting: str,
    contradicting: tuple[str, ...] = (),
    category: str = "schema_contract_mismatch",
) -> dict:
    return {
        "description": "supplier-api now sends camelCase fields.",
        "category": category,
        "supporting_evidence_ids": list(supporting),
        "contradicting_evidence_ids": list(contradicting),
        "missing_evidence": [],
    }


SPEC = document("SPEC-INVOICE-V3#post-v3-invoices", "api_spec")
PAST = document("HIST-INC-044#full-document", "historical_incident")


DEPENDENCY_MAP = EvidenceItem(
    evidence_id="DEPMAP-INVOICE",
    source_type="dependency_map",
    source_name="invoice-processing",
    title="invoice-processing dependency map",
    content="supplier-api -> invoice-transformer -> invoice-workflow",
    metadata={
        "edges": [
            {"from": "supplier-api", "to": "invoice-transformer"},
            {"from": "invoice-transformer", "to": "invoice-workflow"},
        ]
    },
)
FAILURE = log("LOG-882", 43, "ERROR", "invoice-transformer")
UPSTREAM_DEPLOY = deployment(
    "DEPLOY-SOURCE-221", datetime(2026, 7, 15, 8, 5, tzinfo=UTC), "supplier-api"
)
DOWNSTREAM_DEPLOY = deployment(
    "DEPLOY-WORKFLOW-118", datetime(2026, 7, 14, 16, 20, tzinfo=UTC), "invoice-workflow"
)


class FakeRetriever:
    """Returns fixed documents and records every search."""

    def __init__(self, *documents: EvidenceItem) -> None:
        self.documents = list(documents)
        self.calls: list[tuple[str, str]] = []

    def __call__(self, query: str, *, system: str) -> list[EvidenceItem]:
        self.calls.append((query, system))
        return self.documents


class FakeTools:
    """Returns fixed evidence from each tool, and records every call."""

    def __init__(
        self,
        logs: tuple[EvidenceItem, ...] = (),
        deployments: tuple[EvidenceItem, ...] = (),
        maps: tuple[EvidenceItem, ...] = (),
        *,
        truncated: bool = False,
        failing: str | None = None,
    ) -> None:
        self.results = {
            "search_logs": Found(list(logs), truncated),
            "get_deployments": Found(list(deployments)),
            "get_dependency_map": Found(list(maps)),
        }
        self.failing = failing
        self.calls: list[tuple] = []
        self.history: list[ToolCallRecord] = []

    def _answer(self, name: str, *arguments) -> Found:
        self.calls.append((name, *arguments))
        if name == self.failing:
            raise EvidenceUnavailable(f"{name}: timed out")
        return self.results[name]

    async def search_logs(self, start_time, end_time) -> Found:
        return self._answer("search_logs", start_time, end_time)

    async def get_deployments(self, start_time, end_time) -> Found:
        return self._answer("get_deployments", start_time, end_time)

    async def get_dependency_map(self, service) -> Found:
        return self._answer("get_dependency_map", service)


def full_tools(**options) -> FakeTools:
    return FakeTools((FAILURE,), (UPSTREAM_DEPLOY,), (DEPENDENCY_MAP,), **options)


class FakeAudit:
    """Keeps saved records in a list, or fails on request."""

    def __init__(self, error: Exception | None = None) -> None:
        self.records: list = []
        self.error = error

    def save(self, record) -> None:
        if self.error is not None:
            raise self.error
        self.records.append(record)


def dependencies(retriever=None, tools=None, llm=None, audit=None) -> Dependencies:
    return Dependencies(
        retriever=retriever or FakeRetriever(),
        tools=tools or FakeTools(),
        llm=llm or FakeLLM(proposal("LOG-882")),
        audit=audit or FakeAudit(),
    )


def new_graph():
    # Checkpoints in memory, written with the same serializer as the real file.
    return build_graph(InMemorySaver(serde=SERIALIZER))


async def run(
    request=REQUEST, retriever=None, tools=None, llm=None, audit=None, graph=None
):
    return await investigate(
        graph or new_graph(),
        request,
        dependencies(retriever, tools, llm, audit),
        investigation_id="INVEST-1",
    )


def ids(state) -> set[str]:
    # EvidenceItem can't go in a set: its metadata is a dict, which can't be hashed.
    return {item.evidence_id for item in state["evidence"]}


def called(tools: FakeTools, name: str) -> list[tuple]:
    return [call[1:] for call in tools.calls if call[0] == name]


async def test_a_valid_request_becomes_an_incident():
    state = await run()

    assert state["incident"].incident_id == "INC-001"
    assert state["errors"] == ()


async def test_retrieval_searches_the_description_within_the_affected_system():
    retriever = FakeRetriever()

    await run(retriever=retriever)

    assert retriever.calls == [(REQUEST["description"], "invoice-processing")]


async def test_logs_documents_maps_and_deployments_all_become_evidence():
    runbook = document("RB-SCHEMA-COMPAT#full-document")
    tools = FakeTools((FAILURE,), (UPSTREAM_DEPLOY,), (DEPENDENCY_MAP,))

    state = await run(retriever=FakeRetriever(runbook), tools=tools)

    assert ids(state) == {
        "RB-SCHEMA-COMPAT#full-document",
        "LOG-882",
        "DEPMAP-INVOICE",
        "DEPLOY-SOURCE-221",
    }


async def test_logs_are_searched_in_the_incident_window():
    tools = FakeTools()

    await run(tools=tools)

    assert called(tools, "search_logs") == [
        (WINDOW_START, datetime(2026, 7, 15, 11, tzinfo=UTC))
    ]


async def test_the_first_failure_is_the_earliest_error():
    later = log("LOG-886", 48, "ERROR", "invoice-transformer")
    warning = log("LOG-801", 1, "WARN", "invoice-workflow")
    tools = FakeTools((later, warning, FAILURE))

    state = await run(tools=tools)

    assert state["first_failure"] == FAILURE


async def test_deployments_are_searched_in_the_day_before_the_first_failure():
    tools = FakeTools((FAILURE,))

    await run(tools=tools)

    failed_at = FAILURE.timestamp
    assert called(tools, "get_deployments") == [
        (failed_at - timedelta(hours=24), failed_at)
    ]
    assert called(tools, "get_dependency_map") == [("invoice-transformer",)]


async def test_deployments_downstream_of_the_failure_are_dropped():
    tools = FakeTools(
        (FAILURE,), (UPSTREAM_DEPLOY, DOWNSTREAM_DEPLOY), (DEPENDENCY_MAP,)
    )

    state = await run(tools=tools)

    assert UPSTREAM_DEPLOY in state["evidence"]
    assert DOWNSTREAM_DEPLOY not in state["evidence"]


async def test_without_a_map_every_deployment_is_kept():
    tools = FakeTools((FAILURE,), (UPSTREAM_DEPLOY, DOWNSTREAM_DEPLOY))

    state = await run(tools=tools)

    assert {"DEPLOY-SOURCE-221", "DEPLOY-WORKFLOW-118"} <= ids(state)


async def test_without_an_error_deployments_are_searched_before_the_window():
    tools = FakeTools((log("LOG-801", 1, "WARN", "invoice-workflow"),))

    state = await run(tools=tools)

    assert "first_failure" not in state
    assert called(tools, "get_deployments") == [
        (WINDOW_START - timedelta(hours=24), WINDOW_START)
    ]
    assert called(tools, "get_dependency_map") == []


async def test_a_failing_tool_is_recorded_and_the_investigation_continues():
    runbook = document("RB-SCHEMA-COMPAT#full-document")
    tools = FakeTools((FAILURE,), failing="search_logs")

    state = await run(retriever=FakeRetriever(runbook), tools=tools)

    assert state["errors"] == ("log_analysis: search_logs: timed out",)
    assert runbook in state["evidence"]
    assert called(tools, "get_deployments")


async def test_a_failing_dependency_tool_keeps_the_logs():
    tools = FakeTools((FAILURE,), failing="get_deployments")

    state = await run(tools=tools)

    assert state["errors"] == ("dependency_trace: get_deployments: timed out",)
    assert FAILURE in state["evidence"]


async def test_truncated_logs_are_reported():
    state = await run(tools=FakeTools((FAILURE,), truncated=True))

    assert state["errors"] == ("log_analysis: only the earliest logs were returned",)


async def test_an_invalid_request_calls_no_tools():
    retriever = FakeRetriever(document("RB-SCHEMA-COMPAT#full-document"))
    tools = FakeTools((FAILURE,))
    llm = FakeLLM(proposal("LOG-882"))

    state = await run({**REQUEST, "end_time": "2026-07-15T08:00:00Z"}, retriever, tools)

    assert "incident" not in state
    assert state["evidence"] == ()
    assert retriever.calls == []
    assert tools.calls == []
    assert llm.calls == []


async def test_errors_name_each_problem():
    request = {key: value for key, value in REQUEST.items() if key != "description"}

    state = await run({**request, "start_time": "2026-07-15T09:00:00"})

    assert state["errors"] == (
        "description: Field required",
        "start_time: Input should have timezone info",
    )


async def test_errors_do_not_repeat_the_rejected_value():
    state = await run({**REQUEST, "affected_system": "password hunter2"})

    assert state["errors"]
    assert not any("hunter2" in error for error in state["errors"])


async def test_a_missing_request_is_rejected():
    state = await run({})
    assert "incident_id: Field required" in state["errors"]


async def test_evidence_already_in_the_state_is_kept():
    earlier = document("NOTE-1")
    runbook = document("RB-SCHEMA-COMPAT#full-document")

    state = await new_graph().ainvoke(
        {
            "investigation_id": "INVEST-1",
            "started_at": WINDOW_START,
            "request": REQUEST,
            "evidence": (earlier,),
        },
        {"configurable": {"thread_id": "INVEST-1"}},
        context=dependencies(retriever=FakeRetriever(runbook), llm=FakeLLM()),
    )

    assert earlier in state["evidence"]
    assert runbook in state["evidence"]


async def test_selects_a_well_supported_root_cause():
    llm = FakeLLM(proposal("LOG-882", "DEPLOY-SOURCE-221", SPEC.evidence_id))

    state = await run(retriever=FakeRetriever(SPEC), tools=full_tools(), llm=llm)

    best = state["selected_root_cause"]
    assert best.hypothesis_id == "HYP-1"
    assert best.confidence == 0.90
    assert "abstention" not in state


async def test_code_ranks_the_hypotheses_not_the_model():
    llm = FakeLLM(proposal("LOG-882"), proposal("LOG-882", "DEPLOY-SOURCE-221"))

    state = await run(tools=full_tools(), llm=llm)

    assert [item.hypothesis_id for item in state["hypotheses"]] == ["HYP-2", "HYP-1"]
    assert state["selected_root_cause"].hypothesis_id == "HYP-2"


async def test_abstains_when_the_best_hypothesis_scores_too_low():
    state = await run(tools=full_tools(), llm=FakeLLM(proposal("LOG-882")))

    assert "selected_root_cause" not in state
    assert state["abstention"] == "the best hypothesis scored 0.30, below 0.65"
    assert state["hypotheses"][0].confidence == 0.30


async def test_a_hypothesis_exactly_at_the_threshold_is_selected():
    # 0.85 - 0.20 is 0.6499999999999999 in floating point.
    llm = FakeLLM(
        proposal(
            "LOG-882",
            "DEPLOY-SOURCE-221",
            PAST.evidence_id,
            contradicting=(SPEC.evidence_id,),
        )
    )

    state = await run(retriever=FakeRetriever(SPEC, PAST), tools=full_tools(), llm=llm)

    assert state["selected_root_cause"].confidence == 0.65


async def test_a_missing_source_lowers_confidence():
    llm = FakeLLM(proposal("LOG-882", "DEPLOY-SOURCE-221", SPEC.evidence_id))

    state = await run(
        retriever=FakeRetriever(SPEC), tools=full_tools(truncated=True), llm=llm
    )

    best = state["selected_root_cause"]
    assert best.confidence == 0.75
    assert best.confidence_reason.endswith("-0.15 missing evidence")


async def test_abstains_when_the_model_fails():
    llm = FakeLLM(error=LLMError("gemma4:12b failed with 500"))

    state = await run(tools=full_tools(), llm=llm)

    assert state["abstention"] == (
        "the model could not propose a root cause: gemma4:12b failed with 500"
    )
    assert "hypotheses" not in state


async def test_abstains_when_the_model_cites_unknown_evidence():
    state = await run(tools=full_tools(), llm=FakeLLM(proposal("LOG-999")))

    assert "LOG-999" in state["abstention"]
    assert "selected_root_cause" not in state


async def test_abstains_without_calling_the_model_when_there_is_no_evidence():
    llm = FakeLLM(proposal("LOG-882"))

    state = await run(llm=llm)

    assert state["abstention"] == "no evidence was gathered"
    assert llm.calls == []


async def test_root_cause_runs_once_with_evidence_from_every_branch():
    llm = FakeLLM(proposal("LOG-882"))

    await run(retriever=FakeRetriever(SPEC), tools=full_tools(), llm=llm)

    assert len(llm.calls) == 1
    prompt = llm.calls[0][1]
    assert "ID: LOG-882" in prompt
    assert f"ID: {SPEC.evidence_id}" in prompt
    assert "ID: DEPLOY-SOURCE-221" in prompt


async def test_the_incident_takes_the_selected_root_cause_s_category():
    llm = FakeLLM(
        proposal("LOG-882", category="data_quality"),
        proposal("LOG-882", "DEPLOY-SOURCE-221", SPEC.evidence_id),
    )

    state = await run(retriever=FakeRetriever(SPEC), tools=full_tools(), llm=llm)

    assert state["category"] == "schema_contract_mismatch"


async def test_a_low_scoring_hypothesis_leaves_the_category_unknown():
    llm = FakeLLM(proposal("LOG-882", category="networking"))

    state = await run(tools=full_tools(), llm=llm)

    assert state["hypotheses"][0].category == "networking"
    assert state["category"] == "unknown"


async def test_a_failed_model_leaves_the_category_unknown():
    llm = FakeLLM(error=LLMError("gemma4:12b failed with 500"))

    state = await run(tools=full_tools(), llm=llm)

    assert state["category"] == "unknown"


async def test_no_evidence_leaves_the_category_unknown():
    state = await run()

    assert state["category"] == "unknown"


async def test_a_diagnosis_is_audited():
    audit = FakeAudit()
    llm = FakeLLM(proposal("LOG-882", "DEPLOY-SOURCE-221", SPEC.evidence_id))

    state = await run(
        retriever=FakeRetriever(SPEC), tools=full_tools(), llm=llm, audit=audit
    )

    [record] = audit.records
    assert state["status"] == record.status == "diagnosed"
    assert record.investigation_id == "INVEST-1"
    assert record.incident.incident_id == "INC-001"
    assert record.category == "schema_contract_mismatch"
    assert record.selected_hypothesis_id == "HYP-1"
    assert record.hypotheses[0].confidence == 0.90
    assert set(record.evidence_ids) == {
        "LOG-882",
        "DEPLOY-SOURCE-221",
        "DEPMAP-INVOICE",
        SPEC.evidence_id,
    }
    assert record.started_at <= record.finished_at


async def test_an_abstention_is_audited_with_its_reason():
    audit = FakeAudit()

    state = await run(tools=full_tools(), audit=audit)

    [record] = audit.records
    assert state["status"] == record.status == "abstained"
    assert record.abstention == "the best hypothesis scored 0.30, below 0.65"
    assert record.selected_hypothesis_id is None


async def test_a_rejected_request_is_audited_without_its_contents():
    audit = FakeAudit()

    state = await run({**REQUEST, "affected_system": "password hunter2"}, audit=audit)

    [record] = audit.records
    assert state["status"] == record.status == "rejected"
    assert record.incident is None
    assert record.errors
    assert "hunter2" not in record.model_dump_json()


async def test_the_tool_history_is_audited():
    audit = FakeAudit()
    tools = full_tools()
    call = ToolCallRecord(
        tool="search_logs", arguments={}, outcome="ok", items=1, seconds=0.01
    )
    tools.history.append(call)

    await run(tools=tools, audit=audit)

    assert audit.records[0].tool_calls == (call,)


async def test_an_audit_that_cannot_be_saved_fails_the_investigation():
    audit = FakeAudit(error=OSError("disk full"))

    with pytest.raises(OSError, match="disk full"):
        await run(tools=full_tools(), audit=audit)


async def test_each_investigation_gets_a_new_id():
    audit = FakeAudit()

    await investigate(new_graph(), REQUEST, dependencies(audit=audit))
    await investigate(new_graph(), REQUEST, dependencies(audit=audit))

    first, second = (record.investigation_id for record in audit.records)
    assert first != second
    assert first.startswith("INVEST-")


def diagnosing_llm(actions=None, **options) -> FakeLLM:
    return FakeLLM(
        proposal("LOG-882", "DEPLOY-SOURCE-221", SPEC.evidence_id),
        actions=INC_001_PLAN if actions is None else actions,
        **options,
    )


async def test_a_diagnosis_gets_a_validated_plan():
    llm = diagnosing_llm()

    state = await run(retriever=FakeRetriever(SPEC), tools=full_tools(), llm=llm)

    assert [(action.step, action.action) for action in state["actions"]] == [
        (1, "update_field_mapping"),
        (2, "replay_failed_messages"),
        (3, "add_contract_test"),
    ]
    assert state["rejected_actions"] == ()
    assert state["requires_approval"] is True
    assert state["errors"] == ()


async def test_the_catalogue_sets_risk_and_approval():
    state = await run(
        retriever=FakeRetriever(SPEC), tools=full_tools(), llm=diagnosing_llm()
    )

    replay = state["actions"][1]
    assert (replay.risk, replay.changes_state, replay.requires_approval) == (
        "high",
        True,
        True,
    )
    assert replay.rollback


async def test_safe_actions_alone_need_no_approval():
    llm = diagnosing_llm(actions=[step("add_contract_test", "supplier-api")])

    state = await run(retriever=FakeRetriever(SPEC), tools=full_tools(), llm=llm)

    assert [action.action for action in state["actions"]] == ["add_contract_test"]
    assert state["requires_approval"] is False


async def test_an_unsafe_step_is_rejected_and_the_rest_kept():
    llm = diagnosing_llm(
        actions=[
            step("disable_payload_validation", "invoice-transformer"),
            step("update_field_mapping", "invoice-transformer"),
        ]
    )

    state = await run(retriever=FakeRetriever(SPEC), tools=full_tools(), llm=llm)

    [rejected] = state["rejected_actions"]
    assert rejected.proposed.action == "disable_payload_validation"
    assert rejected.problem == "not an allowed action"
    assert [action.action for action in state["actions"]] == ["update_field_mapping"]


async def test_an_abstention_proposes_no_actions():
    llm = FakeLLM(proposal("LOG-882"), actions=INC_001_PLAN)

    state = await run(tools=full_tools(), llm=llm)

    assert "abstention" in state
    assert "actions" not in state
    # Only the root-cause question was asked.
    assert len(llm.calls) == 1


async def test_the_model_is_asked_for_actions_only_after_a_diagnosis():
    llm = diagnosing_llm()

    await run(retriever=FakeRetriever(SPEC), tools=full_tools(), llm=llm)

    first, second = llm.calls
    assert "hypotheses" in first[2]["properties"]
    assert "actions" in second[2]["properties"]


async def test_a_failed_remediation_plans_nothing():
    # An empty plan breaks the schema, which asks for at least one step.
    llm = diagnosing_llm(actions=[])

    state = await run(retriever=FakeRetriever(SPEC), tools=full_tools(), llm=llm)

    assert state["selected_root_cause"].hypothesis_id == "HYP-1"
    assert state["actions"] == ()
    assert state["requires_approval"] is False
    assert state["errors"] == (
        "remediation: the model could not propose actions: "
        "the answer broke the schema in 1 places",
    )


async def test_the_plan_and_its_rejections_are_audited():
    audit = FakeAudit()
    llm = diagnosing_llm(
        actions=[
            step("replay_failed_messages", "invoice-transformer"),
            step("update_field_mapping", "invoice-transformer"),
        ]
    )

    await run(retriever=FakeRetriever(SPEC), tools=full_tools(), llm=llm, audit=audit)

    [record] = audit.records
    assert [action.action for action in record.actions] == ["update_field_mapping"]
    assert record.rejected_actions[0].problem == (
        "must come after a step that fixes the cause"
    )
    assert record.requires_approval is True


THREAD = {"configurable": {"thread_id": "INVEST-1"}}


def decision(choice="approve", comment=""):
    return ApprovalDecision(
        decision=choice,
        approver="sam",
        comment=comment,
        decided_at=WINDOW_START + timedelta(hours=3),
    )


EARLIER_CALL = ToolCallRecord(
    tool="search_logs", arguments={}, outcome="ok", items=1, seconds=0.01
)


async def paused(audit, graph=None):
    graph = graph or new_graph()
    tools = full_tools()
    tools.history.append(EARLIER_CALL)
    state = await run(
        retriever=FakeRetriever(SPEC),
        tools=tools,
        llm=diagnosing_llm(),
        audit=audit,
        graph=graph,
    )
    return graph, state


async def test_a_plan_needing_approval_pauses_the_investigation():
    audit = FakeAudit()

    graph, state = await paused(audit)

    assert state["status"] == "awaiting_approval"
    assert state["__interrupt__"][0].value == {"steps_needing_approval": [1, 2]}
    [record] = audit.records
    assert (record.version, record.status) == (1, "awaiting_approval")
    assert (await graph.aget_state(THREAD)).next == ("approval",)


async def test_a_plan_needing_no_approval_does_not_pause():
    llm = diagnosing_llm(actions=[step("add_contract_test", "supplier-api")])

    state = await run(retriever=FakeRetriever(SPEC), tools=full_tools(), llm=llm)

    assert state["status"] == "diagnosed"
    assert "__interrupt__" not in state


async def test_an_approval_is_saved_as_a_new_version():
    audit = FakeAudit()
    graph, _ = await paused(audit)

    state = await decide(graph, "INVEST-1", decision(), dependencies(audit=audit))

    first, second = audit.records
    assert (second.version, second.status) == (2, "approved")
    assert second.decision == decision()
    assert first.status == "awaiting_approval"
    # The resuming request has new tools, but the calls made before the pause stay.
    assert first.tool_calls == second.tool_calls == (EARLIER_CALL,)
    assert "__interrupt__" not in state


@pytest.mark.parametrize("choice, status", [("reject", "declined")])
async def test_a_refusal_ends_the_investigation(choice, status):
    audit = FakeAudit()
    graph, _ = await paused(audit)

    await decide(
        graph,
        "INVEST-1",
        decision(choice, comment="Check with the supplier team first."),
        dependencies(audit=audit),
    )

    assert [record.status for record in audit.records] == ["awaiting_approval", status]
    assert (await graph.aget_state(THREAD)).next == ()


async def test_resuming_without_a_decision_keeps_it_paused():
    audit = FakeAudit()
    graph, _ = await paused(audit)

    state = await graph.ainvoke(None, THREAD, context=dependencies(audit=audit))

    assert "__interrupt__" in state
    assert [record.status for record in audit.records] == ["awaiting_approval"]


async def test_a_malformed_decision_is_refused():
    audit = FakeAudit()
    graph, _ = await paused(audit)

    with pytest.raises(ValidationError):
        await graph.ainvoke(
            Command(resume={"decision": "approve"}),
            THREAD,
            context=dependencies(audit=audit),
        )

    assert [record.status for record in audit.records] == ["awaiting_approval"]


async def test_a_paused_investigation_survives_a_restart(tmp_path):
    audit = FakeAudit()
    path = tmp_path / "checkpoints.db"

    async with open_checkpointer(path) as checkpointer:
        await paused(audit, build_graph(checkpointer))
    async with open_checkpointer(path) as checkpointer:
        await decide(
            build_graph(checkpointer), "INVEST-1", decision(), dependencies(audit=audit)
        )

    first, second = audit.records
    assert second.status == "approved"
    # Every model in the state came back as itself, not as a plain dict.
    assert second.actions == first.actions
    assert second.selected_hypothesis_id == "HYP-1"


REVIEW = "Check how the supplier contract changed in past incidents."


async def request_more_evidence(audit, graph, retriever=None, llm=None):
    return await decide(
        graph,
        "INVEST-1",
        decision("request_more_evidence", comment=REVIEW),
        dependencies(
            retriever=retriever or FakeRetriever(SPEC, PAST),
            llm=llm or diagnosing_llm(),
            audit=audit,
        ),
    )


async def test_a_request_for_more_evidence_searches_and_reasons_again():
    audit = FakeAudit()
    graph, _ = await paused(audit)
    retriever = FakeRetriever(SPEC, PAST)
    llm = diagnosing_llm()

    state = await request_more_evidence(audit, graph, retriever, llm)

    assert [record.status for record in audit.records] == [
        "awaiting_approval",
        "more_evidence_requested",
        "awaiting_approval",
    ]
    # The reviewer's comment was the search, and only new documents were added.
    assert retriever.calls == [(REVIEW, "invoice-processing")]
    found = [item.evidence_id for item in state["evidence"]]
    assert found.count(SPEC.evidence_id) == 1
    assert PAST.evidence_id in found
    # The model saw the request when it reasoned and planned again.
    assert all(REVIEW in prompt for _, prompt, _ in llm.calls)
    latest = audit.records[-1]
    assert (latest.evidence_round, latest.reviewer_request) == (1, REVIEW)
    assert latest.decision is None


async def test_a_second_request_for_more_evidence_ends_the_investigation():
    audit = FakeAudit()
    graph, _ = await paused(audit)
    await request_more_evidence(audit, graph)

    await request_more_evidence(audit, graph)

    assert audit.records[-1].status == "more_evidence_requested"
    assert (await graph.aget_state(THREAD)).next == ()


async def test_a_follow_up_round_does_not_keep_the_old_plan():
    audit = FakeAudit()
    graph, _ = await paused(audit)

    # This time the best hypothesis is too weak, so FlowGuard abstains.
    await request_more_evidence(audit, graph, llm=FakeLLM(proposal("LOG-882")))

    latest = audit.records[-1]
    assert latest.status == "abstained"
    assert latest.actions == ()
    assert latest.selected_hypothesis_id is None


async def test_a_plan_with_nothing_left_is_tried_again_with_the_reasons():
    llm = diagnosing_llm(
        actions=[step("disable_payload_validation", "invoice-transformer")],
        later_actions=[step("update_field_mapping", "invoice-transformer")],
    )

    state = await run(retriever=FakeRetriever(SPEC), tools=full_tools(), llm=llm)

    assert [action.action for action in state["actions"]] == ["update_field_mapping"]
    [rejected] = state["rejected_actions"]
    assert (rejected.proposed.action, rejected.attempt) == (
        "disable_payload_validation",
        1,
    )
    retry_prompt = llm.calls[2][1]
    assert (
        "Every step of your previous plan was refused:\n"
        "- disable_payload_validation on invoice-transformer: not an allowed action"
    ) in retry_prompt


async def test_a_plan_is_tried_at_most_twice():
    llm = diagnosing_llm(actions=[step("run_shell_command", "invoice-transformer")])

    state = await run(retriever=FakeRetriever(SPEC), tools=full_tools(), llm=llm)

    # One root-cause question and two plans.
    assert len(llm.calls) == 3
    assert [item.attempt for item in state["rejected_actions"]] == [1, 2]
    assert state["actions"] == ()
    assert state["status"] == "diagnosed"


async def test_a_partly_valid_plan_is_kept_without_a_retry():
    llm = diagnosing_llm(
        actions=[
            step("run_shell_command", "invoice-transformer"),
            step("update_field_mapping", "invoice-transformer"),
        ]
    )

    await run(retriever=FakeRetriever(SPEC), tools=full_tools(), llm=llm)

    assert len(llm.calls) == 2


@pytest.mark.parametrize(
    "error, confidence",
    [
        ("remediation: the model could not propose actions: timed out", 0.90),
        ("log_analysis: search_logs: timed out", 0.75),
    ],
)
def test_only_evidence_problems_lower_confidence(error, confidence):
    state = {
        "incident": Incident.model_validate(REQUEST),
        "evidence": (FAILURE, UPSTREAM_DEPLOY, DEPENDENCY_MAP, SPEC),
        "first_failure": FAILURE,
        "errors": (error,),
    }
    llm = FakeLLM(proposal("LOG-882", "DEPLOY-SOURCE-221", SPEC.evidence_id))

    update = root_cause(state, Runtime(context=dependencies(llm=llm)))

    assert update["selected_root_cause"].confidence == confidence


async def test_a_run_that_exceeds_the_step_limit_stops():
    with pytest.raises(GraphRecursionError):
        await investigate(
            new_graph(),
            REQUEST,
            dependencies(retriever=FakeRetriever(SPEC), tools=full_tools()),
            step_limit=3,
        )
