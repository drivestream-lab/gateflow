"""Initiative closure + read-out API routes (ADR-010 §7 / INIT-GATEFLOW-010 W4, INIT-GATEFLOW-011 W2/W4/W5)."""

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
from src.business_services.spec_readout_service import (
    SpecReadoutService,
    get_spec_readout_service,
)
from src.business_services.wave_map_service import WaveMapService, get_wave_map_service
from src.models.closure_models import ClosureStartRequest, ClosureStartResponse
from src.models.initiative_readout_models import (
    InitiativeListResult,
    InitiativeReadout,
)
from src.models.spec_readout_models import SpecReadoutResult
from src.models.wave_map_models import WaveMapResult

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


@router.get(
    "/initiatives/{initiative_id}/waves",
    response_model=WaveMapResult,
)
async def get_initiative_waves(
    initiative_id: str,
    org: Annotated[str, Query(description="Forge org whose board holds the Feature tickets")],
    repo: Annotated[str, Query(description="Forge repo whose board holds the Feature tickets")],
    _: None = Depends(verify_programme_service_token),
    service: WaveMapService = Depends(get_wave_map_service),
) -> WaveMapResult:
    """Per-wave status map from board Feature tickets + runs (CAP-05).

    REQ-14/15/28 — read-only; status ∈ {done, ready-to-start, blocked, active}.
    404 when no run, EPIC, or Feature ticket exists for ``initiative_id``.
    """
    return await service.get_wave_map(initiative_id, org=org, repo=repo)


@router.get(
    "/initiatives/{initiative_id}/spec",
    response_model=SpecReadoutResult,
)
async def get_initiative_spec(
    initiative_id: str,
    org: Annotated[str, Query(description="Forge org whose board holds the EPIC tickets")],
    repo: Annotated[str, Query(description="Forge repo whose board holds the EPIC tickets")],
    _: None = Depends(verify_programme_service_token),
    service: SpecReadoutService = Depends(get_spec_readout_service),
) -> SpecReadoutResult:
    """Spec-lane readout from pin + run state (CAP-04).

    REQ-12/13/28 — Draft Spec PR when ready; plain not-ready before
    ``spec-pr-action`` (never a broken URL). 404 when no run or EPIC exists.
    """
    return await service.get_spec_readout(initiative_id, org=org, repo=repo)
