"""Wave implementation progress DTOs (INIT-GATEFLOW-011 CAP-06 / W6).

REQ-16: task-by-task progress from run timeline; Draft PR link when
``wave-pr-action`` succeeds.
REQ-17: on task failure or run stop (``needs-input``), name which task and why.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ImplementationTaskStatusType(str, Enum):
    """Per-task (pin node / stage) status on the implement-lane timeline."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    STOPPED = "stopped"
    BLOCKED = "blocked"
    FINDINGS = "findings"


class ImplementationTaskItem(BaseModel):
    """One task row derived from a run stage / current workflow node."""

    model_config = ConfigDict(extra="forbid")

    task_id: str = Field(description="Pin / workflow node id (e.g. loop-spec)")
    label: str = Field(description="Plain-language label (pin purpose or node id)")
    status: ImplementationTaskStatusType
    reason: Optional[str] = Field(
        default=None,
        description="Failure/stop reason when status is failed/stopped/blocked/findings",
    )


class ImplementationReadoutResult(BaseModel):
    """GET .../waves/{wave_id}/implementation response."""

    model_config = ConfigDict(extra="forbid")

    initiative_id: str
    wave_id: str
    run_id: Optional[str] = Field(default=None)
    run_status: Optional[str] = Field(default=None)
    workflow_node: Optional[str] = Field(default=None)
    tasks: list[ImplementationTaskItem] = Field(
        default_factory=list,
        description="Per-task timeline from stages (REQ-16 — not a single spinner)",
    )
    draft_pr_number: Optional[int] = Field(
        default=None,
        description="Draft wave PR number when wave-pr-action succeeded; null otherwise",
    )
    draft_pr_url: Optional[str] = Field(
        default=None,
        description="Draft wave PR URL when available; must be null when not",
    )
    failed_task_id: Optional[str] = Field(
        default=None,
        description="Named failing/stopped task when REQ-17 applies",
    )
    failure_reason: Optional[str] = Field(
        default=None,
        description="Why the named task failed or the run stopped (REQ-17)",
    )
    no_run_reason: Optional[str] = Field(
        default=None,
        description="When initiative known but no implement-lane run for this wave",
    )
