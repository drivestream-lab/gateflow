"""Programme-token run status and list APIs (FR-15 / FR-20)."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.api.v1.programme_token import verify_programme_service_token
import src.api.dependencies as api_deps
from src.business_services.metrics_emitter import MetricsEmitter
from src.infra_services.postgres_service import PostgresService
from src.models.adapter_models import RunListResponse
from src.models.control_plane_models import RunStatusResponse

router = APIRouter()


def _get_metrics_emitter() -> MetricsEmitter:
    return api_deps.get_metrics_emitter()


def _get_postgres_service() -> PostgresService:
    return api_deps.get_postgres_service()


@router.get("/runs", response_model=RunListResponse)
async def list_runs(
    initiative_id: Optional[str] = Query(default=None),
    wave_id: Optional[str] = Query(default=None),
    status_type: Optional[str] = Query(default=None),
    org: Optional[str] = Query(default=None),
    repo: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    skip: int = Query(default=0, ge=0),
    _: None = Depends(verify_programme_service_token),
    metrics_emitter: MetricsEmitter = Depends(_get_metrics_emitter),
    postgres_service: PostgresService = Depends(_get_postgres_service),
) -> RunListResponse:
    """List/filter durable runs for programme engineering tools."""
    async with postgres_service.get_session() as session:
        return await metrics_emitter.list_runs(
            session,
            initiative_id=initiative_id,
            wave_id=wave_id,
            status_type=status_type,
            org=org,
            repo=repo,
            limit=limit,
            skip=skip,
        )


@router.get("/runs/{run_id}", response_model=RunStatusResponse)
async def get_run_status(
    run_id: UUID,
    _: None = Depends(verify_programme_service_token),
    metrics_emitter: MetricsEmitter = Depends(_get_metrics_emitter),
    postgres_service: PostgresService = Depends(_get_postgres_service),
) -> RunStatusResponse:
    """Return durable run header + stage/event timeline."""
    async with postgres_service.get_session() as session:
        return await metrics_emitter.get_run_status(session, run_id)
