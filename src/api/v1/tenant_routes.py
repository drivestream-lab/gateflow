"""Tenant registry HTTP routes (INIT-GATEFLOW-012 CAP-01)."""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header

from src.api.v1.tenant_token import verify_tenant_bearer_token
from src.business_services.tenant_service import TenantService, get_tenant_service
from src.models.tenant_models import (
    TenantListResponse,
    TenantReadModel,
    TenantRegisterRequest,
    TenantRegisterResponse,
    TenantResolvedContext,
    TenantUserAttachRequest,
    TenantUserAttachResponse,
)

router = APIRouter(prefix="/tenants")


@router.post("", response_model=TenantRegisterResponse, status_code=200)
async def register_tenant(
    body: TenantRegisterRequest,
    service: TenantService = Depends(get_tenant_service),
) -> TenantRegisterResponse:
    """Register a tenant — public JWT-bypass; no programme/tenant token required."""
    return await service.register_tenant(body)


@router.get("", response_model=TenantListResponse)
async def list_tenants(
    resolved: Annotated[TenantResolvedContext, Depends(verify_tenant_bearer_token)],
    service: TenantService = Depends(get_tenant_service),
) -> TenantListResponse:
    return await service.list_tenants(resolved=resolved)


@router.get("/{tenant_id}", response_model=TenantReadModel)
async def get_tenant(
    tenant_id: UUID,
    resolved: Annotated[TenantResolvedContext, Depends(verify_tenant_bearer_token)],
    service: TenantService = Depends(get_tenant_service),
    x_tenant_identity: Annotated[Optional[str], Header()] = None,
) -> TenantReadModel:
    return await service.get_tenant(
        tenant_id,
        resolved=resolved,
        identity=x_tenant_identity,
    )


@router.post("/{tenant_id}/users", response_model=TenantUserAttachResponse, status_code=200)
async def attach_tenant_user(
    tenant_id: UUID,
    body: TenantUserAttachRequest,
    resolved: Annotated[TenantResolvedContext, Depends(verify_tenant_bearer_token)],
    service: TenantService = Depends(get_tenant_service),
) -> TenantUserAttachResponse:
    return await service.attach_user(tenant_id, body, resolved=resolved)
