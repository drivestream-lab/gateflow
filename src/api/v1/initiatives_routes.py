"""Initiative closure + read-out API routes (ADR-010 §7 / INIT-GATEFLOW-010 W4, INIT-GATEFLOW-011 W2)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from src.api.v1.programme_token import verify_programme_service_token
from src.business_services.closure_start_service import (
    ClosureStartService,
    get_closure_start_service,
)
from src.business_services.initiative_readout_service import (
    InitiativeReadoutService,
    get_initiative_readout_service,
)
from src.models.closure_models import ClosureStartRequest, ClosureStartResponse
from src.models.initiative_readout_models import (
    InitiativeListResult,
    InitiativeReadout,
)

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


@router.get("/initiatives", response_model=InitiativeListResult)
async def list_initiatives(
    org: Annotated[str, Query(description="Forge org whose board holds the EPIC tickets")],
    repo: Annotated[str, Query(description="Forge repo whose board holds the EPIC tickets")],
    _: None = Depends(verify_programme_service_token),
    service: InitiativeReadoutService = Depends(get_initiative_readout_service),
    limit: Annotated[int, Query(ge=1, le=200, description="Max initiatives to return")] = 50,
    skip: Annotated[int, Query(ge=0, description="Initiatives to skip")] = 0,
) -> InitiativeListResult:
    """List initiatives composed from Gateflow-owned data (runs + board EPIC tickets).

    CAP-03 (REQ-09/10) — read-only; ``prd_approval`` is ``unavailable`` until
    the W3 meta bridge wires composed CAP-01 against ``prd-impact-acceptance``.
    """
    return await service.list_initiatives(org=org, repo=repo, limit=limit, skip=skip)


@router.get("/initiatives/{initiative_id}", response_model=InitiativeReadout)
async def get_initiative(
    initiative_id: str,
    org: Annotated[str, Query(description="Forge org whose board holds the EPIC tickets")],
    repo: Annotated[str, Query(description="Forge repo whose board holds the EPIC tickets")],
    _: None = Depends(verify_programme_service_token),
    service: InitiativeReadoutService = Depends(get_initiative_readout_service),
) -> InitiativeReadout:
    """Detail for one initiative composed from Gateflow-owned data (runs + board EPIC).

    404 when no run and no EPIC ticket exists for ``initiative_id`` (REQ-09).
    """
    return await service.get_initiative(initiative_id, org=org, repo=repo)
