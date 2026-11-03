from functools import partial

from flowguard.dataset import load_incident
from flowguard.graph.builder import investigate
from flowguard.graph.context import Dependencies
from flowguard.rag.retrieval import retrieve


def test_inc_001_finds_its_runbook_and_past_incident(client, embedder):
    retriever = partial(retrieve, embedder=embedder, client=client)

    state = investigate(load_incident("INC-001"), Dependencies(retriever=retriever))

    documents = {item.metadata["document_id"] for item in state["evidence"]}
    assert {"RB-SCHEMA-COMPAT", "HIST-INC-044"} <= documents
