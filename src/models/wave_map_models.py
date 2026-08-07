"""Wave map DTOs (INIT-GATEFLOW-011 CAP-05 / W4).

REQ-14: per-wave status ∈ {done, ready-to-start, blocked, active}; when
blocked, names why. REQ-15: derived only from board Feature tickets + run
state — no new wave-state store.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class WaveMapStatusType(str, Enum):
    """Per-wave status vocabulary for CAP-05 wave map (REQ-14)."""

    DONE = "done"
    READY_TO_START = "ready-to-start"
    BLOCKED = "blocked"
    ACTIVE = "active"


class WaveMapItem(BaseModel):
    """One wave row in the initiative wave map."""

    model_config = ConfigDict(extra="forbid")

    wave_id: str = Field(description="Wave id parsed from Feature ticket title, e.g. W0")
    title: str = Field(description="Feature ticket title when known")
    status: WaveMapStatusType
    block_reason: Optional[str] = Field(
        default=None,
        description="Why status is blocked (e.g. predecessor not Done); null otherwise",
    )
    ticket_id: Optional[str] = Field(default=None)
    ticket_url: Optional[str] = Field(default=None)
    board_column: Optional[str] = Field(
        default=None,
        description="Board column when known (Done / In Progress / Todo / …)",
    )
    in_flight_run_id: Optional[str] = Field(
        default=None,
        description="Active run id for this wave when status is active",
    )


class WaveMapResult(BaseModel):
    """GET /api/v1/initiatives/{initiative_id}/waves response."""

    model_config = ConfigDict(extra="forbid")

    initiative_id: str
    waves: list[WaveMapItem] = Field(default_factory=list)
