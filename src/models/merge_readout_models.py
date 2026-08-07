"""Wave merge-confirm readout DTOs (INIT-GATEFLOW-011 CAP-08 / W8).

REQ-21: CAP-01 wave-signoff evidence → merged state + merge commit SHA, or
itemized missing items.
REQ-22: after confirmed merge, nudge when next wave is ready-to-start.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from src.models.checkpoint_models import CheckpointMissingItem, CheckpointVerdictType


class MergeConfirmStateType(str, Enum):
    """Merge-confirm rollup for CAP-08 (REQ-21)."""

    MERGED = "merged"
    NOT_MERGED = "not_merged"
    COULD_NOT_VERIFY = "could_not_verify"


class MergeReadoutResult(BaseModel):
    """GET .../waves/{wave_id}/merge response."""

    model_config = ConfigDict(extra="forbid")

    initiative_id: str
    wave_id: str
    owner: str
    repo: str
    pr_number: Optional[int] = Field(default=None)
    merge_state: MergeConfirmStateType
    merged: bool = Field(default=False)
    merge_commit_sha: Optional[str] = Field(default=None)
    checked_sha: Optional[str] = Field(default=None)
    checked_at: Optional[datetime] = Field(default=None)
    verdict: Optional[CheckpointVerdictType] = Field(default=None)
    missing_items: list[CheckpointMissingItem] = Field(default_factory=list)
    stale_reason: Optional[str] = Field(default=None)
    next_wave_nudge: Optional[str] = Field(
        default=None,
        description='REQ-22 plain nudge, e.g. "wave W9 is now unblocked"',
    )
    no_run_reason: Optional[str] = Field(
        default=None,
        description="When initiative known but no implement-lane run / PR for wave",
    )
