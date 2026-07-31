"""Wave start API routes — implement, spec, and closeout lanes (ADR-010)."""

from fastapi import APIRouter, Depends

from src.api.v1.programme_token import verify_programme_service_token
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
    _: None = Depends(verify_programme_service_token),
    service: WaveStartService = Depends(get_wave_start_service),
) -> WaveStartResponse:
    """Enqueue an authenticated implement-lane run; label triggers are not accepted."""
    return await service.start_implement_wave(body)


@router.post("/waves/spec/start", response_model=WaveStartResponse)
async def start_spec_wave(
    body: SpecWaveStartRequest,
    _: None = Depends(verify_programme_service_token),
    service: WaveStartService = Depends(get_wave_start_service),
) -> WaveStartResponse:
    """Enqueue an authenticated spec-lane run after meta accept-gate."""
    return await service.start_spec_wave(body)


@router.post("/waves/closeout/start", response_model=WaveStartResponse)
async def start_closeout_wave(
    body: CloseoutWaveStartRequest,
    _: None = Depends(verify_programme_service_token),
    service: WaveStartService = Depends(get_wave_start_service),
) -> WaveStartResponse:
    """Enqueue Pass-2 closeout: fixed Enter-at learning-extract; bind existing PR."""
    return await service.start_closeout_wave(body)
