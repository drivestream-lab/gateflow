"""Wave start API routes — implement, spec, and closeout lanes (ADR-010)."""

from fastapi import APIRouter, Depends

from src.common.auth.dependencies import require_role
from src.models.auth_models import AuthContext
from src.models.role_types import RoleType
from src.business_services.wave_start_service import WaveStartService, get_wave_start_service
from src.models.wave_start_models import (
    CloseoutWaveStartRequest,
    ImplementWaveStartRequest,
    SpecWaveStartRequest,
    WaveStartResponse,
)

router = APIRouter()


@router.post("/waves/implement/start", response_model=WaveStartResponse)
async def start_implement_wave(
    body: ImplementWaveStartRequest,
    _auth: AuthContext = Depends(require_role(RoleType.TENANT_ADMIN)),
    service: WaveStartService = Depends(get_wave_start_service),
) -> WaveStartResponse:
    """Enqueue an authenticated implement-lane run; label triggers are not accepted."""
    return await service.start_implement_wave(body)


@router.post("/waves/spec/start", response_model=WaveStartResponse)
async def start_spec_wave(
    body: SpecWaveStartRequest,
    _auth: AuthContext = Depends(require_role(RoleType.TENANT_ADMIN)),
    service: WaveStartService = Depends(get_wave_start_service),
) -> WaveStartResponse:
    """Enqueue an authenticated spec-lane run after meta accept-gate."""
    return await service.start_spec_wave(body)


@router.post("/waves/closeout/start", response_model=WaveStartResponse)
async def start_closeout_wave(
    body: CloseoutWaveStartRequest,
    _auth: AuthContext = Depends(require_role(RoleType.TENANT_ADMIN)),
    service: WaveStartService = Depends(get_wave_start_service),
) -> WaveStartResponse:
    """Enqueue Pass-2 closeout: fixed Enter-at learning-extract; bind existing PR."""
    return await service.start_closeout_wave(body)
