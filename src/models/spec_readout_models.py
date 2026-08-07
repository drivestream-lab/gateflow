"""Spec-lane readout DTOs (INIT-GATEFLOW-011 CAP-04 / W5).

REQ-12: Draft Spec PR link (when ready), generated artifacts, findings/open
questions, exact next step from pin — composed from pin + run state.
REQ-13: before ``spec-pr-action``, plain not-ready message — never a broken URL.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SpecReadoutReadinessType(str, Enum):
    """Readiness of the Draft Spec PR for CAP-04."""

    READY = "ready"
    NOT_READY = "not_ready"
    UNAVAILABLE = "unavailable"


class SpecArtifactItem(BaseModel):
    """One generated artifact observed from a completed stage / handoff."""

    model_config = ConfigDict(extra="forbid")

    workflow_node: str
    label: str = Field(description="Plain-language label for the artifact")
    artifact_path: Optional[str] = Field(
        default=None,
        description="Workspace-relative path when known from handoff; null otherwise",
    )


class SpecReadoutResult(BaseModel):
    """GET /api/v1/initiatives/{initiative_id}/spec response."""

    model_config = ConfigDict(extra="forbid")

    initiative_id: str
    readiness: SpecReadoutReadinessType
    readiness_reason: Optional[str] = Field(
        default=None,
        description="Plain-language reason when not_ready / unavailable (REQ-13)",
    )
    draft_spec_pr_number: Optional[int] = Field(
        default=None,
        description="Draft Spec PR number when readiness=ready; null otherwise",
    )
    draft_spec_pr_url: Optional[str] = Field(
        default=None,
        description="Draft Spec PR URL when ready; must be null when not ready (REQ-13)",
    )
    spec_run_id: Optional[str] = Field(default=None)
    spec_run_status: Optional[str] = Field(default=None)
    workflow_node: Optional[str] = Field(default=None)
    next_step_node_id: Optional[str] = Field(
        default=None,
        description="Exact next pin node id when known",
    )
    next_step_label: Optional[str] = Field(
        default=None,
        description="Plain next-step label (pin purpose or node id)",
    )
    next_step_owner: Optional[str] = Field(default=None)
    generated_artifacts: list[SpecArtifactItem] = Field(default_factory=list)
    findings: list[str] = Field(
        default_factory=list,
        description="Blockers / finding strings from Gateflow-owned handoff / stop context",
    )
    open_questions: list[str] = Field(
        default_factory=list,
        description="Open-question style blockers (e.g. OQ-*) when present",
    )
