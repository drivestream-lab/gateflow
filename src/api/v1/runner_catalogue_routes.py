"""Implemented runner + model catalogue (INIT-GATEFLOW-019)."""

from fastapi import APIRouter, Depends

from src.business_services.runner_catalogue_service import (
    RunnerCatalogueService,
    get_runner_catalogue_service,
)
from src.common.auth.dependencies import require_role
from src.models.auth_models import AuthContext
from src.models.role_types import RoleType
from src.models.runner_catalogue_models import RunnerCatalogueResponse

router = APIRouter()


@router.get("/runners", response_model=RunnerCatalogueResponse)
async def list_runners(
    _auth: AuthContext = Depends(require_role(RoleType.TENANT_ADMIN)),
    service: RunnerCatalogueService = Depends(get_runner_catalogue_service),
) -> RunnerCatalogueResponse:
    """List implemented runners and the models under each runner."""
    return service.list_runners()
