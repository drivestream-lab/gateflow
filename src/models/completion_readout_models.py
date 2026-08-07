"""Initiative completion eligibility DTOs (INIT-GATEFLOW-011 CAP-09 / W8).

REQ-23: ready to close iff every wave is Done; else waiting on wave N;
empty → no waves found.
REQ-24: pure rollup of CAP-05 wave-map data.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from src.models.wave_map_models import WaveMapItem, WaveMapStatusType


class CompletionEligibilityType(str, Enum):
    """Completion eligibility vocabulary (REQ-23)."""

    READY_TO_CLOSE = "ready_to_close"
    WAITING_ON_WAVES = "waiting_on_waves"
    NO_WAVES_FOUND = "no_waves_found"


class CompletionBlockerItem(BaseModel):
    """One wave not yet Done (REQ-23 waiting-on)."""

    model_config = ConfigDict(extra="forbid")

    wave_id: str
    status: WaveMapStatusType
    block_reason: Optional[str] = Field(default=None)


class CompletionReadoutResult(BaseModel):
    """GET /api/v1/initiatives/{initiative_id}/completion response."""

    model_config = ConfigDict(extra="forbid")

    initiative_id: str
    eligibility: CompletionEligibilityType
    message: str = Field(description="Plain-language rollup for clients")
    waiting_on: list[CompletionBlockerItem] = Field(default_factory=list)
    waves: list[WaveMapItem] = Field(
        default_factory=list,
        description="CAP-05 wave-map rows reused for transparency (REQ-24)",
    )
