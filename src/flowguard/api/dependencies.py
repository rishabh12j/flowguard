from collections.abc import AsyncIterator, Callable, Mapping
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from dataclasses import dataclass, field
from functools import partial
from typing import Annotated, Protocol

import httpx
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
from flowguard.rag.ingestion import COLLECTION, ingest, knowledge_chunks
from flowguard.rag.retrieval import retrieve
from flowguard.storage.audit_repository import SqliteAuditStore


class AuditLog(AuditStore, Protocol):
    def get(self, investigation_id: str) -> InvestigationRecord | None: ...

    def history(self, investigation_id: str) -> list[InvestigationRecord]: ...


# A named check that a dependency can serve requests. It returns True when ready.
ReadinessCheck = Callable[[], bool]


@dataclass(frozen=True)
class Services:
    """What every request shares. Tools are not shared: each investigation opens its own."""

    graph: InvestigationGraph
    llm: LLM
    audit: AuditLog
    # Opens new tools, with their own guard and history, for one investigation.
    open_tools: Callable[[], AbstractAsyncContextManager[EvidenceTools]]
    checks: Mapping[str, ReadinessCheck] = field(default_factory=dict)


def document_index(settings: Settings) -> QdrantClient:
    # A Qdrant server keeps the index between restarts. Without one, it's in memory.
    if settings.qdrant_url:
        return QdrantClient(url=settings.qdrant_url)
    return QdrantClient(":memory:")


def ollama_has_model(settings: Settings) -> bool:
    tags = httpx.get(f"{settings.ollama_url}/api/tags", timeout=3).json()
    return any(model["name"] == settings.model for model in tags.get("models", []))


@asynccontextmanager
async def open_services(settings: Settings | None = None) -> AsyncIterator[Services]:
    settings = settings or Settings.from_env()
    embedder = SentenceTransformerEmbedder()
    client = document_index(settings)
    # Indexed at every start, so the index always matches the documents on disk.
    ingest(knowledge_chunks(load_evidence()), embedder, client)
    audit = SqliteAuditStore(settings.audit_db)
    async with open_checkpointer(settings.checkpoint_db) as checkpointer:
        yield Services(
            graph=build_graph(checkpointer),
            llm=OllamaLLM(settings.model, base_url=settings.ollama_url),
            audit=audit,
            open_tools=partial(
                open_evidence_tools, partial(retrieve, embedder=embedder, client=client)
            ),
            checks={
                "documents": lambda: client.count(COLLECTION).count > 0,
                "model": partial(ollama_has_model, settings),
                "audit": lambda: audit.get("readiness-check") is None,
            },
        )


def get_services(request: Request) -> Services:
    services: Services = request.app.state.services
    return services


ServicesDep = Annotated[Services, Depends(get_services)]
