"""Persistence DTO for programme membership grants (INIT-GATEFLOW-017 W0)."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProgrammeMembershipReadModel(BaseModel):
    """Persisted grant pair (identity may enter programme)."""

    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    identity_id: UUID
    programme_id: UUID


class GrantedProgrammeReadModel(BaseModel):
    """Grant pair enriched with the programme tenant binding (session surface).

    Superset of ProgrammeMembershipReadModel: adds the tenant the programme is
    bound to and its display name, so tenant_admin callers can address
    tenant-scoped routes (/api/v1/tenants/{tenant_id}/...) without a
    platform_admin programme read.
    """

    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    identity_id: UUID
    programme_id: UUID
    tenant_id: UUID
    programme_name: str
