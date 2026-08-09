"""Programme connect / catalogue / selection HTTP routes (INIT-GATEFLOW-013 W0/W1)."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from src.api.v1.tenant_token import verify_tenant_bearer_token
from src.business_services.programme_onboarding_service import (
    ProgrammeOnboardingService,
    get_programme_onboarding_service,
)
from src.models.programme_catalogue_models import ProgrammeCatalogueResponse
from src.models.programme_connection_models import (
    ProgrammeConnectRequest,
    ProgrammeConnectResponse,
    ProgrammeConnectionReadModel,
)
from src.models.programme_selection_models import (
    ProgrammeDeselectRequest,
    ProgrammeDeselectResponse,
    ProgrammeSelectRequest,
    ProgrammeSelectResponse,
)
from src.models.tenant_models import TenantResolvedContext

router = APIRouter(prefix="/tenants/{tenant_id}/programme")


@router.put("/connect", response_model=ProgrammeConnectResponse, status_code=200)
async def connect_programme(
    tenant_id: UUID,
    body: ProgrammeConnectRequest,
    resolved: Annotated[TenantResolvedContext, Depends(verify_tenant_bearer_token)],
    service: ProgrammeOnboardingService = Depends(get_programme_onboarding_service),
) -> ProgrammeConnectResponse:
    """Connect (or re-sync) the tenant's single programme meta checkout."""
    return await service.connect_programme(tenant_id, body, resolved=resolved)


@router.get("/connection", response_model=ProgrammeConnectionReadModel)
async def get_programme_connection(
    tenant_id: UUID,
    resolved: Annotated[TenantResolvedContext, Depends(verify_tenant_bearer_token)],
    service: ProgrammeOnboardingService = Depends(get_programme_onboarding_service),
) -> ProgrammeConnectionReadModel:
    return await service.get_connection(tenant_id, resolved=resolved)


@router.get("/catalogue", response_model=ProgrammeCatalogueResponse)
async def get_programme_catalogue(
    tenant_id: UUID,
    resolved: Annotated[TenantResolvedContext, Depends(verify_tenant_bearer_token)],
    service: ProgrammeOnboardingService = Depends(get_programme_onboarding_service),
) -> ProgrammeCatalogueResponse:
    return await service.get_catalogue(tenant_id, resolved=resolved)


@router.post("/repos/select", response_model=ProgrammeSelectResponse, status_code=200)
async def select_programme_repos(
    tenant_id: UUID,
    body: ProgrammeSelectRequest,
    resolved: Annotated[TenantResolvedContext, Depends(verify_tenant_bearer_token)],
    service: ProgrammeOnboardingService = Depends(get_programme_onboarding_service),
) -> ProgrammeSelectResponse:
    """Admit catalogue-gated repos onto the tenant active list (PAT probe on new)."""
    return await service.select_repos(tenant_id, body, resolved=resolved)


@router.post("/repos/deselect", response_model=ProgrammeDeselectResponse, status_code=200)
async def deselect_programme_repo(
    tenant_id: UUID,
    body: ProgrammeDeselectRequest,
    resolved: Annotated[TenantResolvedContext, Depends(verify_tenant_bearer_token)],
    service: ProgrammeOnboardingService = Depends(get_programme_onboarding_service),
) -> ProgrammeDeselectResponse:
    """Remove active-list membership; blocked when an ACTIVE run exists."""
    return await service.deselect_repo(tenant_id, body, resolved=resolved)
