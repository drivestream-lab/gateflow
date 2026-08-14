"""Auth context models for JWT middleware."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.models.identity_status_types import IdentityStatusType
from src.models.programme_membership_models import ProgrammeMembershipReadModel
from src.models.role_types import RoleType


class AuthContext(BaseModel):
    """Authenticated request context set by JWT middleware."""

    model_config = ConfigDict(extra="forbid")

    user_id: UUID = Field(description="Authenticated user identifier")
    tenant_id: Optional[UUID] = Field(default=None, description="Tenant scope when present")
    role: RoleType = Field(description="Role code from JWT")
    owner_id: Optional[UUID] = Field(default=None, description="Owner identifier when applicable")
    session_epoch: int = Field(default=0, description="JWT session epoch compared to identity row")


class LoginRequest(BaseModel):
    """POST /api/auth/login body."""

    model_config = ConfigDict(extra="forbid")

    credential_identifier: str = Field(description="Login identifier (email)")
    password: str = Field(description="Password for the identity")


class LoginResponse(BaseModel):
    """Successful login response carrying a Gateflow-issued JWT and grant snapshot."""

    model_config = ConfigDict(extra="forbid")

    access_token: str = Field(description="Gateflow-issued user JWT")
    token_type: str = Field(default="bearer", description="Bearer token type")
    grants: list[ProgrammeMembershipReadModel] = Field(
        default_factory=list,
        description="Programmes this identity may enter (empty when none granted)",
    )


class EnterProgrammeRequest(BaseModel):
    """POST /api/auth/session/programme body."""

    model_config = ConfigDict(extra="forbid")

    programme_id: UUID = Field(description="Programme the signed-in identity will enter")


class AuthSessionSnapshot(BaseModel):
    """Signed-in identity snapshot (no password, no factory roster, no remint)."""

    model_config = ConfigDict(extra="forbid")

    id: UUID
    display_name: str
    email: str
    status: IdentityStatusType
    role: RoleType
    grants: list[ProgrammeMembershipReadModel] = Field(default_factory=list)
    entered_programme_id: Optional[UUID] = Field(
        default=None,
        description="Programme entered this request; omitted on GET /me",
    )


class UserIdentityReadModel(BaseModel):
    """Persisted user identity (password hash never returned on list/search)."""

    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    credential_identifier: str
    role: RoleType
    display_name: str
    status: IdentityStatusType
    session_epoch: int
    password_hash: str = Field(description="Stored credential hash — internal only")
