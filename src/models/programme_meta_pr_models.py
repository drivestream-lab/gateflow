"""Onboarded programme meta PR DTOs (INIT-GATEFLOW-019)."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProgrammeMetaPrReadModel(BaseModel):
    """One admitted meta PR for a programme."""

    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    programme_id: UUID
    html_url: str
    number: int
    initiative_id: str
    title: str
    created_at: Optional[datetime] = Field(default=None)


class MetaPrOnboardRequest(BaseModel):
    """POST /tenants/{id}/programme/meta/pulls/onboard body."""

    model_config = ConfigDict(extra="forbid")

    html_url: str = Field(min_length=1, description="GitHub HTML URL of the programme meta PR")
