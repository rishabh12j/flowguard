from datetime import UTC, datetime, timedelta

import pytest
from fakes import FakeLLM

from flowguard.domain.audit import ToolCallRecord
from flowguard.domain.evidence import EvidenceItem
from flowguard.graph.builder import GRAPH, investigate
from flowguard.graph.context import Dependencies, EvidenceUnavailable, Found
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


async def run(request=REQUEST, retriever=None, tools=None, llm=None, audit=None):
    return await investigate(
        request, dependencies(retriever, tools, llm, audit), investigation_id="INVEST-1"
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

    state = await GRAPH.ainvoke(
        {
            "investigation_id": "INVEST-1",
            "started_at": WINDOW_START,
            "request": REQUEST,
            "evidence": (earlier,),
        },
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

    await investigate(REQUEST, dependencies(audit=audit))
    await investigate(REQUEST, dependencies(audit=audit))

    first, second = (record.investigation_id for record in audit.records)
    assert first != second
    assert first.startswith("INVEST-")
