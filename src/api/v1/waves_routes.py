"""Wave start API routes (FR-15)."""

from fastapi import APIRouter, Depends

from src.api.v1.programme_token import verify_programme_service_token
from src.business_services.wave_start_service import WaveStartService, get_wave_start_service
from src.models.adapter_models import WaveStartRequest, WaveStartResponse

router = APIRouter()


@router.post("/waves/start", response_model=WaveStartResponse)
async def start_wave(
    body: WaveStartRequest,
    _: None = Depends(verify_programme_service_token),
    service: WaveStartService = Depends(get_wave_start_service),
) -> WaveStartResponse:
    """Enqueue an authenticated wave run; label triggers are not accepted."""
    return await service.start_wave(body)
