"""Wave closeout readout DTOs (INIT-GATEFLOW-011 CAP-07 / W7).

REQ-18: itemized closeout additions (learning / ground stages).
REQ-19: drift vs wave-acceptance baseline SHA (or explicit unknown).
REQ-20: drift is advisory only — never blocks closeout mechanics.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CloseoutDriftStatusType(str, Enum):
    """Advisory drift outcome for CAP-07 (REQ-19 / REQ-20)."""

    NONE = "none"
    DRIFTED = "drifted"
    UNKNOWN_NO_BASELINE = "unknown_no_baseline"
    UNAVAILABLE = "unavailable"


class CloseoutAdditionKindType(str, Enum):
    """Kinds of closeout additions listed for REQ-18."""

    LEARNING_ITEM = "learning_item"
    LEARNING_EXTRACT = "learning_extract"
    GROUND_STAGE = "ground_stage"
    ARTIFACT = "artifact"


class CloseoutAdditionItem(BaseModel):
    """One itemized addition observed from Gateflow-owned closeout evidence."""

    model_config = ConfigDict(extra="forbid")

    kind: CloseoutAdditionKindType
    label: str
    detail: Optional[str] = Field(default=None)
    reference: Optional[str] = Field(
        default=None,
        description="Item key, stage node, or artifact path when known",
    )


class CloseoutReadoutResult(BaseModel):
    """GET .../waves/{wave_id}/closeout response."""

    model_config = ConfigDict(extra="forbid")

    initiative_id: str
    wave_id: str
    run_id: Optional[str] = Field(default=None)
    run_status: Optional[str] = Field(default=None)
    additions: list[CloseoutAdditionItem] = Field(default_factory=list)
    drift_status: CloseoutDriftStatusType = Field(
        default=CloseoutDriftStatusType.UNAVAILABLE,
        description="Advisory drift status (REQ-19); never blocks mechanics (REQ-20)",
    )
    drift_message: Optional[str] = Field(
        default=None,
        description="Plain-language drift / unknown-baseline message",
    )
    baseline_sha: Optional[str] = Field(
        default=None,
        description="wave-acceptance checkpoint_check checked_sha when known",
    )
    closeout_head_sha: Optional[str] = Field(
        default=None,
        description="Current Draft PR head SHA at readout time when known",
    )
    advisory_only: bool = Field(
        default=True,
        description="Always true — drift does not mutate closeout (REQ-20)",
    )
    no_run_reason: Optional[str] = Field(
        default=None,
        description="When initiative known but no implement-lane run for this wave",
    )
