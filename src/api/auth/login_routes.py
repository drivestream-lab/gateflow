"""Login and session routes for Gateflow-issued user JWTs (INIT-GATEFLOW-017 W3)."""

from fastapi import APIRouter, Depends, Request

from src.business_services.auth_identity_service import (
    AuthIdentityService,
    get_auth_identity_service,
)
from src.common.auth.dependencies import assert_live_session, get_auth_context
from src.models.auth_models import (
    AuthContext,
    AuthSessionSnapshot,
    EnterProgrammeRequest,
    LoginRequest,
    LoginResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


async def require_live_auth(request: Request) -> AuthContext:
    """Bearer JWT plus live identity session (epoch / status)."""
    return await assert_live_session(get_auth_context(request))


@router.post("/login", response_model=LoginResponse, status_code=200)
async def login(
    body: LoginRequest,
    service: AuthIdentityService = Depends(get_auth_identity_service),
) -> LoginResponse:
    """Exchange credentials for a Gateflow-issued user JWT and grant snapshot (no UI)."""
    return await service.login(body)


@router.get("/me", response_model=AuthSessionSnapshot, status_code=200)
async def me(
    auth: AuthContext = Depends(require_live_auth),
    service: AuthIdentityService = Depends(get_auth_identity_service),
) -> AuthSessionSnapshot:
    """Return the signed-in identity snapshot (no password, no factory roster)."""
    return await service.me(auth)


@router.post("/session/programme", response_model=AuthSessionSnapshot, status_code=200)
async def enter_programme(
    body: EnterProgrammeRequest,
    auth: AuthContext = Depends(require_live_auth),
    service: AuthIdentityService = Depends(get_auth_identity_service),
) -> AuthSessionSnapshot:
    """Enter a granted programme without reminting the JWT."""
    return await service.enter_programme(auth, body.programme_id)
