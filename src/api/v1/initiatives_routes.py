"""Initiative closure + read-out API routes (ADR-010 §7 / INIT-GATEFLOW-010 W4, INIT-GATEFLOW-011 W2/W4–W8)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from src.api.v1.programme_token import verify_programme_service_token
from src.business_services.closure_start_service import (
    ClosureStartService,
    get_closure_start_service,
)
from src.business_services.closeout_readout_service import (
    CloseoutReadoutService,
    get_closeout_readout_service,
)
from src.business_services.completion_readout_service import (
    CompletionReadoutService,
    get_completion_readout_service,
)
from src.business_services.implementation_readout_service import (
    ImplementationReadoutService,
    get_implementation_readout_service,
)
from src.business_services.initiative_readout_service import (
    InitiativeReadoutService,
    get_initiative_readout_service,
)
from src.business_services.merge_readout_service import (
    MergeReadoutService,
    get_merge_readout_service,
)
from src.business_services.spec_readout_service import (
    SpecReadoutService,
    get_spec_readout_service,
)
from src.business_services.wave_map_service import WaveMapService, get_wave_map_service
from src.models.closeout_readout_models import CloseoutReadoutResult
from src.models.closure_models import ClosureStartRequest, ClosureStartResponse
from src.models.completion_readout_models import CompletionReadoutResult
from src.models.implementation_readout_models import ImplementationReadoutResult
from src.models.initiative_readout_models import (
    InitiativeListResult,
    InitiativeReadout,
)
from src.models.merge_readout_models import MergeReadoutResult
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
    "/initiatives/{initiative_id}/waves/{wave_id}/implementation",
    response_model=ImplementationReadoutResult,
)
async def get_wave_implementation(
    initiative_id: str,
    wave_id: str,
    org: Annotated[str, Query(description="Forge org whose board holds the EPIC tickets")],
    repo: Annotated[str, Query(description="Forge repo whose board holds the EPIC tickets")],
    _: None = Depends(verify_programme_service_token),
    service: ImplementationReadoutService = Depends(get_implementation_readout_service),
) -> ImplementationReadoutResult:
    """Wave implement-lane progress from run timeline (CAP-06).

    REQ-16/17/28 — per-task progress + Draft PR when present; named failure on
    stop; GET-only. 404 when no run or EPIC exists for ``initiative_id``.
    """
    return await service.get_implementation_readout(initiative_id, wave_id, org=org, repo=repo)


@router.get(
    "/initiatives/{initiative_id}/waves/{wave_id}/closeout",
    response_model=CloseoutReadoutResult,
)
async def get_wave_closeout(
    initiative_id: str,
    wave_id: str,
    org: Annotated[str, Query(description="Forge org whose board holds the EPIC tickets")],
    repo: Annotated[str, Query(description="Forge repo whose board holds the EPIC tickets")],
    _: None = Depends(verify_programme_service_token),
    service: CloseoutReadoutService = Depends(get_closeout_readout_service),
) -> CloseoutReadoutResult:
    """Wave closeout additions + advisory drift (CAP-07).

    REQ-18/19/20/28 — learning/ground itemization; drift vs acceptance baseline
    (unknown when missing); advisory only; GET-only.
    """
    return await service.get_closeout_readout(initiative_id, wave_id, org=org, repo=repo)


@router.get(
    "/initiatives/{initiative_id}/waves/{wave_id}/merge",
    response_model=MergeReadoutResult,
)
async def get_wave_merge(
    initiative_id: str,
    wave_id: str,
    org: Annotated[str, Query(description="Forge org whose board holds the EPIC tickets")],
    repo: Annotated[str, Query(description="Forge repo whose board holds the EPIC tickets")],
    _: None = Depends(verify_programme_service_token),
    service: MergeReadoutService = Depends(get_merge_readout_service),
) -> MergeReadoutResult:
    """Wave merge confirm via CAP-01 wave-signoff (CAP-08).

    REQ-21/22/28 — merged + merge SHA or missing items; next-wave nudge;
    GET-only.
    """
    return await service.get_merge_readout(initiative_id, wave_id, org=org, repo=repo)


@router.get(
    "/initiatives/{initiative_id}/completion",
    response_model=CompletionReadoutResult,
)
async def get_initiative_completion(
    initiative_id: str,
    org: Annotated[str, Query(description="Forge org whose board holds the Feature tickets")],
    repo: Annotated[str, Query(description="Forge repo whose board holds the Feature tickets")],
    _: None = Depends(verify_programme_service_token),
    service: CompletionReadoutService = Depends(get_completion_readout_service),
) -> CompletionReadoutResult:
    """Completion eligibility as CAP-05 wave-map rollup (CAP-09).

    REQ-23/24/28 — ready to close iff all waves Done; no waves found when empty;
    GET-only.
    """
    return await service.get_completion_readout(initiative_id, org=org, repo=repo)


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
