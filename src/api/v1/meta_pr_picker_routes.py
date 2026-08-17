"""Tenant-scoped meta PR picker (INIT-GATEFLOW-019 CAP-A)."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.business_services.meta_pr_picker_service import (
    META_PR_PICKER_LIMIT,
    MetaPrPickerService,
    get_meta_pr_picker_service,
)
from src.common.auth.dependencies import require_tenant_resolved
from src.models.meta_pr_picker_models import MetaPrPickerItem, MetaPrPickerResponse
from src.models.programme_meta_pr_models import MetaPrOnboardRequest
from src.models.tenant_models import TenantResolvedContext

router = APIRouter(prefix="/tenants/{tenant_id}/programme")


@router.get("/meta/pulls", response_model=MetaPrPickerResponse)
async def list_programme_meta_pulls(
    tenant_id: UUID,
    resolved: Annotated[TenantResolvedContext, Depends(require_tenant_resolved)],
    service: MetaPrPickerService = Depends(get_meta_pr_picker_service),
    skip: int = Query(default=0, ge=0, description="INIT-derived rows to skip"),
    limit: int = Query(
        default=META_PR_PICKER_LIMIT,
        ge=1,
        le=META_PR_PICKER_LIMIT,
        description="Last N INIT-derived meta PRs (max 10)",
    ),
    refresh: bool = Query(
        default=False,
        description="Skip Redis, fetch GitHub, rewrite the last-10 cache",
    ),
) -> MetaPrPickerResponse:
    """List the last 10 INIT-* meta PRs with live CAP-01 and spec-run join."""
    return await service.list_meta_prs(tenant_id, resolved, skip=skip, limit=limit, refresh=refresh)


@router.get("/meta/pulls/onboarded", response_model=MetaPrPickerResponse)
async def list_onboarded_programme_meta_pulls(
    tenant_id: UUID,
    resolved: Annotated[TenantResolvedContext, Depends(require_tenant_resolved)],
    service: MetaPrPickerService = Depends(get_meta_pr_picker_service),
) -> MetaPrPickerResponse:
    """List meta PRs admitted for Gateflow operations."""
    return await service.list_onboarded_meta_prs(tenant_id, resolved)


@router.post("/meta/pulls/onboard", response_model=MetaPrPickerItem)
async def onboard_programme_meta_pull(
    tenant_id: UUID,
    body: MetaPrOnboardRequest,
    resolved: Annotated[TenantResolvedContext, Depends(require_tenant_resolved)],
    service: MetaPrPickerService = Depends(get_meta_pr_picker_service),
) -> MetaPrPickerItem:
    """Admit one INIT-* meta PR. Idempotent when already onboarded."""
    return await service.onboard_meta_pr(tenant_id, resolved, body)
