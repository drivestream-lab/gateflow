"""Programme-token run metrics API (FR-13) + skill efficacy (CAP-02)."""

from typing import Optional

from fastapi import APIRouter, Depends, Query

import src.api.dependencies as api_deps
from src.business_services.metrics_emitter import MetricsEmitter
from src.business_services.skill_efficacy_service import SkillEfficacyService
from src.common.auth.dependencies import require_role
from src.infra_services.postgres_service import PostgresService
from src.models.auth_models import AuthContext
from src.models.control_plane_models import RunMetricsResponse
from src.models.role_types import RoleType
from src.models.skill_efficacy_models import SkillEfficacyResponse

router = APIRouter()


def _get_metrics_emitter() -> MetricsEmitter:
    return api_deps.get_metrics_emitter()


def _get_skill_efficacy_service() -> SkillEfficacyService:
    return api_deps.get_skill_efficacy_service()


def _get_postgres_service() -> PostgresService:
    return api_deps.get_postgres_service()


@router.get("/metrics/runs", response_model=RunMetricsResponse)
async def get_run_metrics(
    _auth: AuthContext = Depends(require_role(RoleType.TENANT_ADMIN)),
    metrics_emitter: MetricsEmitter = Depends(_get_metrics_emitter),
    postgres_service: PostgresService = Depends(_get_postgres_service),
) -> RunMetricsResponse:
    """Aggregate stage duration p50/p95 by workflow_node within retention window."""
    async with postgres_service.get_session() as session:
        return await metrics_emitter.aggregate_run_metrics(session)


@router.get("/metrics/skill-efficacy", response_model=SkillEfficacyResponse)
async def get_skill_efficacy(
    model_id: Optional[str] = Query(default=None, description="Filter by model_id"),
    prompt_revision: Optional[str] = Query(default=None, description="Filter by prompt_revision"),
    auth: AuthContext = Depends(require_role(RoleType.TENANT_ADMIN)),
    skill_efficacy_service: SkillEfficacyService = Depends(_get_skill_efficacy_service),
    postgres_service: PostgresService = Depends(_get_postgres_service),
) -> SkillEfficacyResponse:
    """Tenant-scoped skill/spec efficacy rates (CAP-02 / REQ-04–REQ-10)."""
    assert auth.tenant_id is not None
    async with postgres_service.get_session() as session:
        return await skill_efficacy_service.get_skill_efficacy(
            session,
            tenant_id=auth.tenant_id,
            model_id=model_id,
            prompt_revision=prompt_revision,
        )
