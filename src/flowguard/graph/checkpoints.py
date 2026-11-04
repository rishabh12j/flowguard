from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import aiosqlite
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from flowguard.domain.approval import ApprovalDecision
from flowguard.domain.audit import ToolCallRecord
from flowguard.domain.evidence import EvidenceItem
from flowguard.domain.hypotheses import RootCauseHypothesis
from flowguard.domain.incidents import Incident
from flowguard.domain.remediation import PlannedAction, ProposedAction, RejectedAction

# Every class the investigation state can hold. Loading a checkpoint rebuilds only
# these, so a tampered checkpoint file can't create an arbitrary object. Anything
# missing from this list comes back as a plain dict.
STATE_TYPES = (
    Incident,
    EvidenceItem,
    RootCauseHypothesis,
    ProposedAction,
    PlannedAction,
    RejectedAction,
    ToolCallRecord,
    ApprovalDecision,
)
SERIALIZER = JsonPlusSerializer(
    allowed_msgpack_modules=[
        (type_.__module__, type_.__name__) for type_ in STATE_TYPES
    ]
)


@asynccontextmanager
async def open_checkpointer(path: str | Path) -> AsyncIterator[AsyncSqliteSaver]:
    """Keeps paused investigations in a SQLite file, so they survive a restart."""
    async with aiosqlite.connect(path) as connection:
        yield AsyncSqliteSaver(connection, serde=SERIALIZER)
