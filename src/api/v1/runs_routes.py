"""Programme-token run status API (FR-15)."""

from uuid import UUID

from fastapi import APIRouter, Depends

import src.api.dependencies as api_deps
from src.api.v1.programme_token import verify_programme_service_token
from src.business_services.metrics_emitter import MetricsEmitter
from src.infra_services.postgres_service import PostgresService
from src.models.control_plane_models import RunStatusResponse

router = APIRouter()


def _get_metrics_emitter() -> MetricsEmitter:
    return api_deps.get_metrics_emitter()


def _get_postgres_service() -> PostgresService:
    return api_deps.get_postgres_service()


@router.get("/runs/{run_id}", response_model=RunStatusResponse)
async def get_run_status(
    run_id: UUID,
    _: None = Depends(verify_programme_service_token),
    metrics_emitter: MetricsEmitter = Depends(_get_metrics_emitter),
    postgres_service: PostgresService = Depends(_get_postgres_service),
) -> RunStatusResponse:
    """Return durable run header for programme engineering tools."""
    async with postgres_service.get_session() as session:
        return await metrics_emitter.get_run_status(session, run_id)
