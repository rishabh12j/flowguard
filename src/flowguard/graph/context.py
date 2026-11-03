from dataclasses import dataclass
from typing import Protocol

from flowguard.domain.evidence import EvidenceItem


class Retriever(Protocol):
    def __call__(self, query: str, *, system: str) -> list[EvidenceItem]: ...


@dataclass(frozen=True)
class Dependencies:
    retriever: Retriever
