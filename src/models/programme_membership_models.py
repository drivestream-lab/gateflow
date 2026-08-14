"""Persistence DTO for programme membership grants (INIT-GATEFLOW-017 W0)."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProgrammeMembershipReadModel(BaseModel):
    """Persisted grant pair (identity may enter programme)."""

    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    identity_id: UUID
    programme_id: UUID
