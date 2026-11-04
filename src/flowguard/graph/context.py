from dataclasses import dataclass
from datetime import datetime
from typing import NamedTuple, Protocol

from flowguard.domain.evidence import EvidenceItem


class EvidenceUnavailable(Exception):
    """A tool could not provide evidence: it failed, timed out, or was denied."""


class Found(NamedTuple):
    items: list[EvidenceItem]
    # True when the tool returned only part of what matched.
    truncated: bool = False


class Retriever(Protocol):
    def __call__(self, query: str, *, system: str) -> list[EvidenceItem]: ...


class EvidenceTools(Protocol):
    async def search_logs(self, start_time: datetime, end_time: datetime) -> Found: ...

    async def get_deployments(
        self, start_time: datetime, end_time: datetime
    ) -> Found: ...

    async def get_dependency_map(self, service: str) -> Found: ...


@dataclass(frozen=True)
class Dependencies:
    retriever: Retriever
    tools: EvidenceTools
