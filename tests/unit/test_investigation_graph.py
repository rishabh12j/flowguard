from flowguard.domain.evidence import EvidenceItem
from flowguard.graph.builder import GRAPH, investigate
from flowguard.graph.context import Dependencies

REQUEST = {
    "incident_id": "INC-001",
    "description": "Invoice INV-2048 did not enter the approval workflow.",
    "affected_system": "invoice-processing",
    "start_time": "2026-07-15T09:00:00Z",
    "end_time": "2026-07-15T11:00:00Z",
}


def document(evidence_id: str) -> EvidenceItem:
    return EvidenceItem(
        evidence_id=evidence_id,
        source_type="runbook",
        source_name="invoice-transformer",
        title="A runbook",
        content="Some steps.",
        metadata={},
        retrieval_score=0.7,
    )


class FakeRetriever:
    """Returns fixed documents and records every search."""

    def __init__(self, *documents: EvidenceItem) -> None:
        self.documents = list(documents)
        self.calls: list[tuple[str, str]] = []

    def __call__(self, query: str, *, system: str) -> list[EvidenceItem]:
        self.calls.append((query, system))
        return self.documents


def run(request, retriever=None):
    retriever = retriever or FakeRetriever()
    return investigate(request, Dependencies(retriever=retriever))


def test_a_valid_request_becomes_an_incident():
    state = run(REQUEST)

    assert state["incident"].incident_id == "INC-001"
    assert state["errors"] == ()


def test_retrieval_searches_the_description_within_the_affected_system():
    retriever = FakeRetriever()

    run(REQUEST, retriever)

    assert retriever.calls == [(REQUEST["description"], "invoice-processing")]


def test_retrieved_documents_become_evidence():
    runbook = document("RB-SCHEMA-COMPAT#full-document")

    state = run(REQUEST, FakeRetriever(runbook))

    assert state["evidence"] == (runbook,)


def test_an_invalid_request_stops_before_retrieval():
    retriever = FakeRetriever(document("RB-SCHEMA-COMPAT#full-document"))

    state = run({**REQUEST, "end_time": "2026-07-15T08:00:00Z"}, retriever)

    assert "incident" not in state
    assert state["evidence"] == ()
    assert retriever.calls == []


def test_errors_name_each_problem():
    request = {key: value for key, value in REQUEST.items() if key != "description"}

    state = run({**request, "start_time": "2026-07-15T09:00:00"})

    assert state["errors"] == (
        "description: Field required",
        "start_time: Input should have timezone info",
    )


def test_errors_do_not_repeat_the_rejected_value():
    state = run({**REQUEST, "affected_system": "password hunter2"})

    assert state["errors"]
    assert not any("hunter2" in error for error in state["errors"])


def test_a_missing_request_is_rejected():
    state = GRAPH.invoke({}, context=Dependencies(retriever=FakeRetriever()))

    assert "incident_id: Field required" in state["errors"]


def test_evidence_already_in_the_state_is_kept():
    earlier = document("LOG-882")
    runbook = document("RB-SCHEMA-COMPAT#full-document")

    state = GRAPH.invoke(
        {"request": REQUEST, "evidence": (earlier,)},
        context=Dependencies(retriever=FakeRetriever(runbook)),
    )

    assert state["evidence"] == (earlier, runbook)
