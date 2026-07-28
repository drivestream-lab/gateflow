"""Forge authorize API — explicit external-action mutate gate (ADR-009 W2)."""

from uuid import UUID

from fastapi import APIRouter, Depends

from src.api.v1.programme_token import verify_programme_service_token
from src.business_services.forge_action_service import (
    ForgeActionService,
    get_forge_action_service,
)
from src.models.forge_models import ForgeAuthorizeRequest, ForgeAuthorizeResponse

router = APIRouter()


@router.post(
    "/runs/{run_id}/forge/authorize",
    response_model=ForgeAuthorizeResponse,
)
async def authorize_forge_action(
    run_id: UUID,
    body: ForgeAuthorizeRequest,
    _: None = Depends(verify_programme_service_token),
    service: ForgeActionService = Depends(get_forge_action_service),
) -> ForgeAuthorizeResponse:
    """Execute pending external-action forge after explicit authorization.

    Run must be STOPPED at a pin ``external-action`` with ``forge.action``.
    Does not Cursor-dispatch forge skills.
    """
    return await service.authorize_and_execute(run_id, body)
