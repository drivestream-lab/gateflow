"""Platform agent catalogue DTOs (INIT-GATEFLOW-014 W1)."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.models.lane_types import LaneType


class AgentCatalogueProvisionRequest(BaseModel):
    """Provision (or re-provision) a platform agent catalogue runner."""

    model_config = ConfigDict(extra="forbid")

    runner_id: str = Field(min_length=1, description="Stable runner id (e.g. cursor)")
    credential: str = Field(min_length=1, description="Agent API credential (plaintext)")
    display_name: Optional[str] = Field(default=None, description="Optional display label")


class AgentCatalogueEntryReadModel(BaseModel):
    """Catalogue row without credential on ordinary reads."""

    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    runner_id: str
    display_name: Optional[str] = None
    has_credential: bool = Field(description="True when a usable credential is stored")


class EffectiveRunner(BaseModel):
    """Resolved runner + model + credential for a lane start."""

    model_config = ConfigDict(extra="forbid")

    runner_id: str
    model_id: Optional[str] = None
    credential: str = Field(description="Catalogue credential — never log")
    lane: LaneType
    source: str = Field(description="caller_override | lane_default")
