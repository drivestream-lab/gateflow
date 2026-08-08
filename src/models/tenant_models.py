"""Tenant registry DTOs (INIT-GATEFLOW-012 CAP-01 / REQ-01–09, REQ-32)."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TenantRepoRef(BaseModel):
    """Registered org/repo pair under a tenant."""

    model_config = ConfigDict(extra="forbid")

    org: str = Field(min_length=1)
    repo: str = Field(min_length=1)


class TenantBoardDefault(BaseModel):
    """Optional default programme board for a tenant (REQ-08)."""

    model_config = ConfigDict(extra="forbid")

    project_owner: str = Field(min_length=1)
    project_number: int = Field(gt=0)


class TenantRegisterRequest(BaseModel):
    """POST /api/v1/tenants body."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, description="Tenant display name")
    pat: str = Field(min_length=1, description="GitHub PAT (never echoed in responses)")
    repos: list[TenantRepoRef] = Field(min_length=1)
    workspace_root: str = Field(
        min_length=1,
        description="Absolute path for tenant workspaces",
    )
    board: Optional[TenantBoardDefault] = Field(
        default=None,
        description="Optional default board project_owner/project_number",
    )


class TenantRegisterResponse(BaseModel):
    """Registration success — bearer token returned once."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: UUID
    name: str
    bearer_token: str = Field(description="Tenant-scoped bearer token (one-time return)")
    repos: list[TenantRepoRef]
    workspace_root: str
    board: Optional[TenantBoardDefault] = None


class TenantUserAttachRequest(BaseModel):
    """POST /api/v1/tenants/{tenant_id}/users body."""

    model_config = ConfigDict(extra="forbid")

    identity: str = Field(
        min_length=1,
        description="User identity (email or handle)",
    )


class TenantUserAttachResponse(BaseModel):
    """User attach success."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: UUID
    identity: str


class TenantReadModel(BaseModel):
    """Tenant detail/list item — never includes pat (REQ-02 / REQ-32)."""

    model_config = ConfigDict(extra="forbid", from_attributes=True)

    tenant_id: UUID
    name: str
    repos: list[TenantRepoRef]
    workspace_root: str
    board: Optional[TenantBoardDefault] = None


class TenantListResponse(BaseModel):
    """GET /api/v1/tenants."""

    model_config = ConfigDict(extra="forbid")

    tenants: list[TenantReadModel]


class TenantRepoProbeFailure(BaseModel):
    """Per-repo PAT probe failure detail (REQ-06)."""

    model_config = ConfigDict(extra="forbid")

    org: str
    repo: str
    reason: str


class PatProbeResult(BaseModel):
    """ok/reason pair from github_pat_probe (TDD §3.2)."""

    model_config = ConfigDict(extra="forbid")

    ok: bool
    reason: Optional[str] = None


class TenantResolvedContext(BaseModel):
    """Resolved tenant from bearer token (does not populate JWT auth context)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: UUID
    name: str


class TenantBoardResolveRequest(BaseModel):
    """Internal helper input for REQ-08 board default resolution."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: Optional[UUID] = None
    project_number: Optional[int] = Field(default=None)
    project_owner: Optional[str] = Field(default=None)

    @model_validator(mode="after")
    def positive_project_number_when_set(self) -> "TenantBoardResolveRequest":
        if self.project_number is not None and self.project_number <= 0:
            raise ValueError("project_number must be a positive integer when set")
        return self
