"""Initiative closure API routes (ADR-010 §7 / INIT-GATEFLOW-010 W4)."""

from fastapi import APIRouter, Depends, status

from src.api.v1.programme_token import verify_programme_service_token
from src.business_services.closure_start_service import (
    ClosureStartService,
    get_closure_start_service,
)
from src.models.closure_models import ClosureStartRequest, ClosureStartResponse

router = APIRouter()


@router.post(
    "/initiatives/closure/start",
    response_model=ClosureStartResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def start_initiative_closure(
    body: ClosureStartRequest,
    _: None = Depends(verify_programme_service_token),
    service: ClosureStartService = Depends(get_closure_start_service),
) -> ClosureStartResponse:
    """Enqueue initiative-closure: Done-gate, EPIC Done, fixed Enter-at purge-app."""
    return await service.start_closure(body)
