from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import APIRouter, Body, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict, ValidationError

from flowguard.api.dependencies import Services, ServicesDep
from flowguard.domain.approval import ApprovalDecision, Decision
from flowguard.domain.audit import DuplicateVersion, InvestigationRecord
from flowguard.graph.builder import decide, investigate
from flowguard.graph.context import Dependencies, EvidenceTools
from flowguard.graph.nodes.intake import describe

router = APIRouter(prefix="/investigations")


class DecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    approver: str
    comment: str = ""


def dependencies(services: Services, tools: EvidenceTools) -> Dependencies:
    return Dependencies(
        tools=tools,
        llm=services.llm,
        audit=services.audit,
    )


def latest(services: Services, investigation_id: str) -> InvestigationRecord:
    record = services.audit.get(investigation_id)
    if record is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="investigation not found")
    return record


@router.post("", status_code=status.HTTP_201_CREATED)
async def start_investigation(
    # A plain object, not an Incident, so the graph validates it and audits a rejection.
    body: Annotated[dict[str, Any], Body()],
    services: ServicesDep,
    response: Response,
) -> InvestigationRecord:
    async with services.open_tools() as tools:
        state = await investigate(services.graph, body, dependencies(services, tools))

    # Read back what was saved, so the response is exactly what was audited.
    record = latest(services, state["investigation_id"])
    if record.status == "rejected":
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, detail=record.model_dump(mode="json")
        )
    response.headers["Location"] = f"/investigations/{record.investigation_id}"
    return record


@router.get("/{investigation_id}")
def get_investigation(
    investigation_id: str, services: ServicesDep
) -> InvestigationRecord:
    return latest(services, investigation_id)


@router.get("/{investigation_id}/events")
def get_events(
    investigation_id: str, services: ServicesDep
) -> list[InvestigationRecord]:
    versions = services.audit.history(investigation_id)
    if not versions:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="investigation not found")
    return versions


async def record_decision(
    investigation_id: str,
    decision: Decision,
    request: DecisionRequest,
    services: Services,
) -> InvestigationRecord:
    # Only a paused investigation can be decided, and only once.
    current = latest(services, investigation_id)
    if current.status != "awaiting_approval":
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail=f"the investigation is {current.status}, not awaiting approval",
        )
    try:
        decided = ApprovalDecision(
            decision=decision,
            approver=request.approver,
            comment=request.comment,
            decided_at=datetime.now(UTC),
        )
    except ValidationError as error:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=[describe(problem) for problem in error.errors()],
        ) from error

    if not await resume(services, investigation_id, decided):
        raise HTTPException(
            status.HTTP_409_CONFLICT, detail="another decision was recorded first"
        )
    return latest(services, investigation_id)


async def resume(
    services: Services, investigation_id: str, decided: ApprovalDecision
) -> bool:
    """Resumes the investigation, or returns False if another decision won the race."""
    # The MCP clients wrap any exception raised inside this block in an
    # ExceptionGroup, so the conflict is caught here and reported outside it.
    async with services.open_tools() as tools:
        try:
            await decide(
                services.graph, investigation_id, decided, dependencies(services, tools)
            )
        except DuplicateVersion:
            # Another decision was saved between the status check and this one.
            return False
    return True


@router.post("/{investigation_id}/approve")
async def approve(
    investigation_id: str, request: DecisionRequest, services: ServicesDep
) -> InvestigationRecord:
    return await record_decision(investigation_id, "approve", request, services)


@router.post("/{investigation_id}/reject")
async def reject(
    investigation_id: str, request: DecisionRequest, services: ServicesDep
) -> InvestigationRecord:
    return await record_decision(investigation_id, "reject", request, services)


@router.post("/{investigation_id}/request-more-evidence")
async def request_more_evidence(
    investigation_id: str, request: DecisionRequest, services: ServicesDep
) -> InvestigationRecord:
    return await record_decision(
        investigation_id, "request_more_evidence", request, services
    )
