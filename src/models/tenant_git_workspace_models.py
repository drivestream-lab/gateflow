"""Tenant git workspace resolve DTOs (INIT-GATEFLOW-012 CAP-02 / REQ-10–15)."""

from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WorkspaceResolveModeType(str, Enum):
    """Closed vocabulary for clone-vs-fetch outcome (TDD §8)."""

    CLONED = "cloned"
    FETCHED = "fetched"


class TenantWorkspaceCredential(BaseModel):
    """Internal lookup of tenant + stored PAT for a registered org/repo.

    Never returned from HTTP read/list routes (REQ-32 / G1).
    """

    model_config = ConfigDict(extra="forbid")

    tenant_id: UUID
    workspace_root: str = Field(min_length=1)
    pat: str = Field(min_length=1)
    org: str = Field(min_length=1)
    repo: str = Field(min_length=1)


class WorkspaceResolveResult(BaseModel):
    """Absolute workspace path plus clone/fetch mode."""

    model_config = ConfigDict(extra="forbid")

    path: str = Field(min_length=1, description="Absolute workspace checkout path")
    mode: WorkspaceResolveModeType
