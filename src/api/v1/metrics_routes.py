"""Programme-token run metrics API (FR-13)."""

from fastapi import APIRouter, Depends

import src.api.dependencies as api_deps
from src.api.v1.programme_token import verify_programme_service_token
from src.business_services.metrics_emitter import MetricsEmitter
from src.infra_services.postgres_service import PostgresService
from src.models.control_plane_models import RunMetricsResponse

router = APIRouter()


def _get_metrics_emitter() -> MetricsEmitter:
    return api_deps.get_metrics_emitter()


def _get_postgres_service() -> PostgresService:
    return api_deps.get_postgres_service()


@router.get("/metrics/runs", response_model=RunMetricsResponse)
async def get_run_metrics(
    _: None = Depends(verify_programme_service_token),
    metrics_emitter: MetricsEmitter = Depends(_get_metrics_emitter),
    postgres_service: PostgresService = Depends(_get_postgres_service),
) -> RunMetricsResponse:
    """Aggregate stage duration p50/p95 by workflow_node within retention window."""
    async with postgres_service.get_session() as session:
        return await metrics_emitter.aggregate_run_metrics(session)
