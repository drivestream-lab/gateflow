"""Auth context models for JWT middleware."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.models.role_types import RoleType


class AuthContext(BaseModel):
    """Authenticated request context set by JWT middleware."""

    model_config = ConfigDict(extra="forbid")

    user_id: UUID = Field(description="Authenticated user identifier")
    tenant_id: Optional[UUID] = Field(default=None, description="Tenant scope when present")
    role: RoleType = Field(description="Role code from JWT")
    owner_id: Optional[UUID] = Field(default=None, description="Owner identifier when applicable")


class LoginRequest(BaseModel):
    """POST /api/auth/login body."""

    model_config = ConfigDict(extra="forbid")

    credential_identifier: str = Field(description="Login identifier (e.g. email)")
    password: str = Field(description="Password for the identity")


class LoginResponse(BaseModel):
    """Successful login response carrying a Gateflow-issued JWT."""

    model_config = ConfigDict(extra="forbid")

    access_token: str = Field(description="Gateflow-issued user JWT")
    token_type: str = Field(default="bearer", description="Bearer token type")


class UserIdentityReadModel(BaseModel):
    """Persisted user identity (password hash never returned)."""

    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    credential_identifier: str
    role: RoleType
    tenant_id: Optional[UUID] = Field(default=None)
    password_hash: str = Field(description="Stored credential hash — internal only")
