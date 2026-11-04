from typing import Annotated, Any

from fastapi import APIRouter, Body, HTTPException, Response, status

from flowguard.api.dependencies import ServicesDep
from flowguard.domain.audit import InvestigationRecord
from flowguard.graph.builder import investigate
from flowguard.graph.context import Dependencies

router = APIRouter(prefix="/investigations")


@router.post("", status_code=status.HTTP_201_CREATED)
async def start_investigation(
    # A plain object, not an Incident, so the graph validates it and audits a rejection.
    body: Annotated[dict[str, Any], Body()],
    services: ServicesDep,
    response: Response,
) -> InvestigationRecord:
    async with services.open_tools() as tools:
        dependencies = Dependencies(
            retriever=services.retriever,
            tools=tools,
            llm=services.llm,
            audit=services.audit,
        )
        state = await investigate(body, dependencies)

    # Read back what was saved, so the response is exactly what was audited.
    record = services.audit.get(state["investigation_id"])
    if record is None:
        raise RuntimeError("the investigation finished without an audit record")
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
    record = services.audit.get(investigation_id)
    if record is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="investigation not found")
    return record
