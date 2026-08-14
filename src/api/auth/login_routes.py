"""Login routes for Gateflow-issued user JWTs (INIT-GATEFLOW-017 W0)."""

from fastapi import APIRouter, Depends

from src.business_services.auth_identity_service import (
    AuthIdentityService,
    get_auth_identity_service,
)
from src.models.auth_models import LoginRequest, LoginResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse, status_code=200)
async def login(
    body: LoginRequest,
    service: AuthIdentityService = Depends(get_auth_identity_service),
) -> LoginResponse:
    """Exchange credentials for a Gateflow-issued user JWT and grant snapshot (no UI)."""
    return await service.login(body)
