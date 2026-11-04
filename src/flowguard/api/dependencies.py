from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from dataclasses import dataclass
from functools import partial
from typing import Annotated, Protocol

from fastapi import Depends, Request
from qdrant_client import QdrantClient

from flowguard.config import Settings
from flowguard.dataset import load_evidence
from flowguard.domain.audit import InvestigationRecord
from flowguard.graph.builder import InvestigationGraph, build_graph
from flowguard.graph.checkpoints import open_checkpointer
from flowguard.graph.context import AuditStore, EvidenceTools
from flowguard.llm.client import LLM, OllamaLLM
from flowguard.mcp.evidence_tools import open_evidence_tools
from flowguard.rag.embedding import SentenceTransformerEmbedder
from flowguard.rag.ingestion import ingest, knowledge_chunks
from flowguard.rag.retrieval import retrieve
from flowguard.storage.audit_repository import SqliteAuditStore


class AuditLog(AuditStore, Protocol):
    def get(self, investigation_id: str) -> InvestigationRecord | None: ...

    def history(self, investigation_id: str) -> list[InvestigationRecord]: ...


@dataclass(frozen=True)
class Services:
    """What every request shares. Tools are not shared: each investigation opens its own."""

    graph: InvestigationGraph
    llm: LLM
    audit: AuditLog
    # Opens new tools, with their own guard and history, for one investigation.
    open_tools: Callable[[], AbstractAsyncContextManager[EvidenceTools]]


@asynccontextmanager
async def open_services(settings: Settings | None = None) -> AsyncIterator[Services]:
    settings = settings or Settings.from_env()
    embedder = SentenceTransformerEmbedder()
    # Qdrant runs in memory until Docker Compose adds a server, so the documents
    # are indexed every time the API starts.
    client = QdrantClient(":memory:")
    ingest(knowledge_chunks(load_evidence()), embedder, client)
    async with open_checkpointer(settings.checkpoint_db) as checkpointer:
        yield Services(
            graph=build_graph(checkpointer),
            llm=OllamaLLM(),
            audit=SqliteAuditStore(settings.audit_db),
            open_tools=partial(
                open_evidence_tools, partial(retrieve, embedder=embedder, client=client)
            ),
        )


def get_services(request: Request) -> Services:
    services: Services = request.app.state.services
    return services


ServicesDep = Annotated[Services, Depends(get_services)]
