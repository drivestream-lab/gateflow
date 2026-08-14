"""platform_admin Programme + agent catalogue routes (INIT-GATEFLOW-014 W1)."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.business_services.identity_directory_service import (
    IdentityDirectoryService,
    get_identity_directory_service,
)
from src.business_services.platform_agent_catalogue_service import (
    PlatformAgentCatalogueService,
    get_platform_agent_catalogue_service,
)
from src.business_services.programme_service import ProgrammeService, get_programme_service
from src.business_services.programme_wipe_service import (
    ProgrammeWipeService,
    get_programme_wipe_service,
)
from src.common.auth.dependencies import require_directory_admin, require_role
from src.models.agent_catalogue_models import (
    AgentCatalogueEntryReadModel,
    AgentCatalogueProvisionRequest,
    EffectiveRunner,
)
from src.models.auth_models import AuthContext
from src.models.identity_models import IdentityGrantRequest, IdentityReadModel
from src.models.lane_types import LaneType
from src.models.programme_membership_models import ProgrammeMembershipReadModel
from src.models.programme_models import (
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


@programme_router.post(
    "/{programme_id}/catalogue/refresh",
    response_model=ProgrammeReadModel,
)
async def refresh_programme_catalogue(
    programme_id: UUID,
    _auth: AuthContext = Depends(require_role(RoleType.PLATFORM_ADMIN)),
    service: ProgrammeService = Depends(get_programme_service),
) -> ProgrammeReadModel:
    """Fetch meta and rewrite persisted repo_catalogue (REQ-49). Select/onboard stay tenant_admin."""
    return await service.refresh_catalogue(programme_id)


@programme_router.post("/{programme_id}/wipe", response_model=ProgrammeWipeResult)
async def wipe_programme(
    programme_id: UUID,
    _auth: AuthContext = Depends(require_role(RoleType.PLATFORM_ADMIN)),
    service: ProgrammeWipeService = Depends(get_programme_wipe_service),
) -> ProgrammeWipeResult:
    """Wipe programme + child tenant + shared secrets (REQ-35); refuse mid-run (REQ-46)."""
    return await service.wipe_programme(programme_id)


@programme_router.post("/{programme_id}/grants", response_model=ProgrammeMembershipReadModel)
async def grant_programme_identity(
    programme_id: UUID,
    body: IdentityGrantRequest,
    _auth: AuthContext = Depends(require_directory_admin),
    service: IdentityDirectoryService = Depends(get_identity_directory_service),
) -> ProgrammeMembershipReadModel:
    return await service.grant(programme_id, body.identity_id)


@programme_router.delete(
    "/{programme_id}/grants/{identity_id}",
    response_model=ProgrammeMembershipReadModel,
)
async def detach_programme_identity(
    programme_id: UUID,
    identity_id: UUID,
    _auth: AuthContext = Depends(require_directory_admin),
    service: IdentityDirectoryService = Depends(get_identity_directory_service),
) -> ProgrammeMembershipReadModel:
    return await service.detach(programme_id, identity_id)


@programme_router.get("/{programme_id}/grants", response_model=list[IdentityReadModel])
async def list_programme_members(
    programme_id: UUID,
    _auth: AuthContext = Depends(require_directory_admin),
    service: IdentityDirectoryService = Depends(get_identity_directory_service),
) -> list[IdentityReadModel]:
    return await service.list_members(programme_id)


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
