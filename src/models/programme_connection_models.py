"""Programme connection DTOs (INIT-GATEFLOW-013 CAP-01 / REQ-01–04, REQ-28)."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProgrammeConnectRequest(BaseModel):
    """POST …/programme/connect body."""

    model_config = ConfigDict(extra="forbid")

    org: str = Field(min_length=1, description="Programme meta org")
    repo: str = Field(min_length=1, description="Programme meta repo")
    ref: Optional[str] = Field(
        default=None,
        description="Optional git ref to checkout after clone/fetch",
    )


class ProgrammeConnectionReadModel(BaseModel):
    """Persisted programme connection — never includes PAT."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: UUID
    org: str
    repo: str
    ref: Optional[str] = None
    last_synced_at: datetime


class ProgrammeConnectResponse(BaseModel):
    """Connect success response."""

    model_config = ConfigDict(extra="forbid")

    connection: ProgrammeConnectionReadModel


class ProgrammeCatalogueRefreshResponse(BaseModel):
    """Catalogue refresh success — programme meta re-synced; selections untouched."""

    model_config = ConfigDict(extra="forbid")

    connection: ProgrammeConnectionReadModel
