"""Runs API under JWT (INIT-GATEFLOW-014 W2)."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query

import src.api.dependencies as api_deps
from src.business_services.metrics_emitter import MetricsEmitter
from src.common.auth.dependencies import require_role
from src.infra_services.postgres_service import PostgresService
from src.models.adapter_models import RunListResponse
from src.models.auth_models import AuthContext
from src.models.control_plane_models import RunStatusResponse
from src.models.role_types import RoleType

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
    auth: AuthContext = Depends(require_role(RoleType.TENANT_ADMIN)),
    metrics_emitter: MetricsEmitter = Depends(_get_metrics_emitter),
    postgres_service: PostgresService = Depends(_get_postgres_service),
) -> RunListResponse:
    """List/filter durable runs scoped to the caller's tenant (ADR-016)."""
    async with postgres_service.get_session() as session:
        return await metrics_emitter.list_runs(
            session,
            tenant_id=auth.tenant_id,
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
    auth: AuthContext = Depends(require_role(RoleType.TENANT_ADMIN)),
    metrics_emitter: MetricsEmitter = Depends(_get_metrics_emitter),
    postgres_service: PostgresService = Depends(_get_postgres_service),
) -> RunStatusResponse:
    """Return durable run header + stage/event timeline for the caller's tenant."""
    async with postgres_service.get_session() as session:
        return await metrics_emitter.get_run_status(session, run_id, tenant_id=auth.tenant_id)
