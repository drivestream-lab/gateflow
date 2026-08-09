"""Programme connect / catalogue HTTP routes (INIT-GATEFLOW-013 W0)."""

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
