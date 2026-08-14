"""platform_admin factory identity directory routes (INIT-GATEFLOW-017 W1)."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.business_services.identity_directory_service import (
    IdentityDirectoryService,
    get_identity_directory_service,
)
from src.common.auth.dependencies import require_directory_admin
from src.models.auth_models import AuthContext
from src.models.identity_models import (
    IdentityEnterRequest,
    IdentityPasswordSetRequest,
    IdentityReadModel,
)
from src.models.programme_membership_models import ProgrammeMembershipReadModel

identity_router = APIRouter(prefix="/identities", tags=["Identities"])


@identity_router.post("", response_model=IdentityReadModel)
async def enter_identity(
    body: IdentityEnterRequest,
    _auth: AuthContext = Depends(require_directory_admin),
    service: IdentityDirectoryService = Depends(get_identity_directory_service),
) -> IdentityReadModel:
    return await service.enter_identity(body)


@identity_router.get("", response_model=list[IdentityReadModel])
async def list_identities(
    q: Optional[str] = Query(default=None, description="Name contains or email exact"),
    _auth: AuthContext = Depends(require_directory_admin),
    service: IdentityDirectoryService = Depends(get_identity_directory_service),
) -> list[IdentityReadModel]:
    return await service.list_identities(q)


@identity_router.post("/{identity_id}/suspend", response_model=IdentityReadModel)
async def suspend_identity(
    identity_id: UUID,
    _auth: AuthContext = Depends(require_directory_admin),
    service: IdentityDirectoryService = Depends(get_identity_directory_service),
) -> IdentityReadModel:
    return await service.suspend_identity(identity_id)


@identity_router.post("/{identity_id}/unsuspend", response_model=IdentityReadModel)
async def unsuspend_identity(
    identity_id: UUID,
    _auth: AuthContext = Depends(require_directory_admin),
    service: IdentityDirectoryService = Depends(get_identity_directory_service),
) -> IdentityReadModel:
    return await service.unsuspend_identity(identity_id)


@identity_router.put("/{identity_id}/password", response_model=IdentityReadModel)
async def set_identity_password(
    identity_id: UUID,
    body: IdentityPasswordSetRequest,
    _auth: AuthContext = Depends(require_directory_admin),
    service: IdentityDirectoryService = Depends(get_identity_directory_service),
) -> IdentityReadModel:
    return await service.set_password(identity_id, body)


@identity_router.get("/{identity_id}/grants", response_model=list[ProgrammeMembershipReadModel])
async def list_identity_grants(
    identity_id: UUID,
    _auth: AuthContext = Depends(require_directory_admin),
    service: IdentityDirectoryService = Depends(get_identity_directory_service),
) -> list[ProgrammeMembershipReadModel]:
    return await service.list_grants(identity_id)
