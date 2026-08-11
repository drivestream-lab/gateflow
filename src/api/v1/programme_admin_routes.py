"""platform_admin Programme + agent catalogue routes (INIT-GATEFLOW-014 W1)."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.business_services.platform_agent_catalogue_service import (
    PlatformAgentCatalogueService,
    get_platform_agent_catalogue_service,
)
from src.business_services.programme_service import ProgrammeService, get_programme_service
from src.business_services.programme_wipe_service import (
    ProgrammeWipeService,
    get_programme_wipe_service,
)
from src.common.auth.dependencies import require_role
from src.models.agent_catalogue_models import (
    AgentCatalogueEntryReadModel,
    AgentCatalogueProvisionRequest,
    EffectiveRunner,
)
from src.models.auth_models import AuthContext
from src.models.lane_types import LaneType
from src.models.programme_models import (
    AttachTenantAdminRequest,
    AttachTenantAdminResponse,
    ProgrammeCreateResult,
    ProgrammeLaneDefaultsUpdateRequest,
    ProgrammeOnboardRequest,
    ProgrammeReadModel,
    ProgrammeWipeResult,
)
from src.models.role_types import RoleType

programme_router = APIRouter(prefix="/programmes", tags=["Programmes"])
agent_catalogue_router = APIRouter(prefix="/agent-catalogue", tags=["AgentCatalogue"])


@programme_router.post("", response_model=ProgrammeCreateResult)
async def create_programme(
    body: ProgrammeOnboardRequest,
    _auth: AuthContext = Depends(require_role(RoleType.PLATFORM_ADMIN)),
    service: ProgrammeService = Depends(get_programme_service),
) -> ProgrammeCreateResult:
    return await service.validate_then_create(body)


@programme_router.get("", response_model=list[ProgrammeReadModel])
async def list_programmes(
    _auth: AuthContext = Depends(require_role(RoleType.PLATFORM_ADMIN)),
    service: ProgrammeService = Depends(get_programme_service),
) -> list[ProgrammeReadModel]:
    return await service.list_programmes()


@programme_router.get("/{programme_id}", response_model=ProgrammeReadModel)
async def get_programme(
    programme_id: UUID,
    _auth: AuthContext = Depends(require_role(RoleType.PLATFORM_ADMIN)),
    service: ProgrammeService = Depends(get_programme_service),
) -> ProgrammeReadModel:
    return await service.get_programme(programme_id)


@programme_router.post("/{programme_id}/wipe", response_model=ProgrammeWipeResult)
async def wipe_programme(
    programme_id: UUID,
    _auth: AuthContext = Depends(require_role(RoleType.PLATFORM_ADMIN)),
    service: ProgrammeWipeService = Depends(get_programme_wipe_service),
) -> ProgrammeWipeResult:
    """Wipe programme + child tenant + shared secrets (REQ-35); refuse mid-run (REQ-46)."""
    return await service.wipe_programme(programme_id)


@programme_router.post("/{programme_id}/tenant-admins", response_model=AttachTenantAdminResponse)
async def attach_tenant_admin(
    programme_id: UUID,
    body: AttachTenantAdminRequest,
    _auth: AuthContext = Depends(require_role(RoleType.PLATFORM_ADMIN)),
    service: ProgrammeService = Depends(get_programme_service),
) -> AttachTenantAdminResponse:
    return await service.attach_tenant_admin(programme_id, body)


@programme_router.put("/{programme_id}/lane-defaults", response_model=ProgrammeReadModel)
async def set_lane_defaults(
    programme_id: UUID,
    body: ProgrammeLaneDefaultsUpdateRequest,
    _auth: AuthContext = Depends(require_role(RoleType.PLATFORM_ADMIN)),
    service: ProgrammeService = Depends(get_programme_service),
) -> ProgrammeReadModel:
    return await service.set_lane_defaults(programme_id, body)


@programme_router.get("/{programme_id}/effective-runner", response_model=EffectiveRunner)
async def resolve_effective_runner(
    programme_id: UUID,
    lane: LaneType = Query(..., description="Delivery lane"),
    caller_runner: Optional[str] = Query(default=None),
    caller_model: Optional[str] = Query(default=None),
    _auth: AuthContext = Depends(require_role(RoleType.PLATFORM_ADMIN)),
    service: PlatformAgentCatalogueService = Depends(get_platform_agent_catalogue_service),
) -> EffectiveRunner:
    return await service.resolve_effective_runner(
        programme_id,
        lane,
        caller_runner=caller_runner,
        caller_model=caller_model,
    )


@agent_catalogue_router.post("", response_model=AgentCatalogueEntryReadModel)
async def provision_agent(
    body: AgentCatalogueProvisionRequest,
    _auth: AuthContext = Depends(require_role(RoleType.PLATFORM_ADMIN)),
    service: PlatformAgentCatalogueService = Depends(get_platform_agent_catalogue_service),
) -> AgentCatalogueEntryReadModel:
    return await service.provision(body)


@agent_catalogue_router.get("", response_model=list[AgentCatalogueEntryReadModel])
async def list_agent_catalogue(
    _auth: AuthContext = Depends(require_role(RoleType.PLATFORM_ADMIN)),
    service: PlatformAgentCatalogueService = Depends(get_platform_agent_catalogue_service),
) -> list[AgentCatalogueEntryReadModel]:
    return await service.list_entries()
