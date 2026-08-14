"""Factory identity directory DTOs (INIT-GATEFLOW-017 W1). Password is write-only."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.models.identity_status_types import IdentityStatusType
from src.models.programme_membership_models import ProgrammeMembershipReadModel
from src.models.role_types import RoleType


class IdentityEnterRequest(BaseModel):
    """POST /api/v1/identities body."""

    model_config = ConfigDict(extra="forbid")

    display_name: str = Field(description="Display label (required, not unique)")
    email: str = Field(description="Login identifier (unique email)")
    password: str = Field(description="Initial password (never returned)")


class IdentityPasswordSetRequest(BaseModel):
    """PUT /api/v1/identities/{id}/password body."""

    model_config = ConfigDict(extra="forbid")

    password: str = Field(description="Replacement password (never returned)")


class IdentityGrantRequest(BaseModel):
    """POST /api/v1/programmes/{id}/grants body."""

    model_config = ConfigDict(extra="forbid")

    identity_id: UUID = Field(description="Existing factory identity to grant")


class IdentityReadModel(BaseModel):
    """Factory identity as returned on list/search/enter (no password)."""

    model_config = ConfigDict(extra="forbid")

    id: UUID
    display_name: str
    email: str
    status: IdentityStatusType
    role: RoleType
    grants: list[ProgrammeMembershipReadModel] = Field(default_factory=list)


class IdentityListQuery(BaseModel):
    """Optional list/search query (name contains or email exact, case-insensitive)."""

    model_config = ConfigDict(extra="forbid")

    q: Optional[str] = Field(default=None, description="Search query")
