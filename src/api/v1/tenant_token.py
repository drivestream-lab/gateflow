"""Tenant-scoped bearer dependency (ADR-011 Option A — fourth trust zone)."""

from typing import Annotated

from fastapi import Depends, Header

from src.business_services.tenant_service import TenantService, get_tenant_service
from src.exceptions.app_exceptions import UnauthorizedError
from src.models.tenant_models import TenantResolvedContext


async def verify_tenant_bearer_token(
    authorization: Annotated[str | None, Header()] = None,
    tenant_service: TenantService = Depends(get_tenant_service),
) -> TenantResolvedContext:
    """Validate Bearer against stored per-tenant tokens; do not set JWT auth context."""
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedError(message="Missing or invalid tenant bearer token")
    token = authorization[7:].strip()
    if not token:
        raise UnauthorizedError(message="Missing tenant bearer token")
    resolved = await tenant_service.resolve_tenant_by_token(token)
    if resolved is None:
        raise UnauthorizedError(message="Invalid tenant bearer token")
    return resolved
