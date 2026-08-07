"""Closure preview DTOs (INIT-GATEFLOW-011 CAP-10 / W9).

REQ-25: pre-purge planned delete vs keep from purge skill allowlist.
REQ-26: post-purge actual deleted/kept from purge-app handoff signals.
REQ-27: CAP-01 reuse for closure signoff checkpoints (nested results).
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from src.models.checkpoint_models import CheckpointStatusResult

# App layout defaults matching purge-initiative-artifacts-app / profile.
_REPORTS_DIR = "docs/specification/reports"
_ADR_DIR = "docs/specification/adr"
_PRODUCT_SPEC_DIR = "docs/specification/product"

# Normative plan_source citation (REQ-25 — do not invent deletes).
PURGE_PLAN_SOURCE = (
    "prayog-skills/references/artifact-write-contract.md"
    " + purge-initiative-artifacts-app allowlist"
)


class PurgePreviewPhaseType(str, Enum):
    """Whether purge-app has executed for this initiative (REQ-25 / REQ-26)."""

    NOT_YET_RUN = "not_yet_run"
    PURGE_EXECUTED = "purge_executed"


class PurgePlanPreview(BaseModel):
    """Planned delete vs keep from the purge skill's own allowlist (REQ-25)."""

    model_config = ConfigDict(extra="forbid")

    planned_delete: list[str] = Field(
        description="PURGE allowlist path patterns scoped to the initiative",
    )
    planned_keep: list[str] = Field(
        description="KEEP / refuse-delete path patterns (must never be deleted)",
    )
    plan_source: str = Field(
        default=PURGE_PLAN_SOURCE,
        description="Citation of purge skill / artifact-write-contract SSOT",
    )


class PurgeExecutionPreview(BaseModel):
    """Actual lists after purge-app ran (REQ-26) — from handoff signals."""

    model_config = ConfigDict(extra="forbid")

    deleted: list[str] = Field(default_factory=list)
    kept: list[str] = Field(
        default_factory=list,
        description="Paths refused as KEEP (signals.refused)",
    )
    missing_ok: list[str] = Field(
        default_factory=list,
        description="Allowlisted paths already absent (idempotent missing_ok)",
    )


class ClosurePreviewResult(BaseModel):
    """GET /api/v1/initiatives/{initiative_id}/closure response."""

    model_config = ConfigDict(extra="forbid")

    initiative_id: str
    owner: str
    repo: str
    purge_phase: PurgePreviewPhaseType
    purge_phase_message: str = Field(
        description='Human label; "not yet run" when purge-app has not executed',
    )
    plan: PurgePlanPreview
    execution: Optional[PurgeExecutionPreview] = Field(
        default=None,
        description="Present only when purge_phase is purge_executed",
    )
    closure_pr_number: Optional[int] = Field(default=None)
    signoff_app: Optional[CheckpointStatusResult] = Field(
        default=None,
        description="CAP-01 evaluate for initiative-closure-signoff-app when PR exists",
    )
    signoff_meta: Optional[CheckpointStatusResult] = Field(
        default=None,
        description="CAP-01 evaluate for initiative-closure-signoff-meta when PR exists",
    )
    no_closure_run_reason: Optional[str] = Field(
        default=None,
        description="When initiative known but no closure-lane run yet",
    )


def build_purge_plan_preview(initiative_id: str) -> PurgePlanPreview:
    """Project purge-app allowlist/refuse rules for one INIT (REQ-25).

    Path patterns match ``purge-initiative-artifacts-app`` / artifact-write-contract
    — Gateflow does not invent an independent delete list.
    """
    init = initiative_id.strip()
    planned_delete = [
        f"{_REPORTS_DIR}/Initiative-Feasibility-Report-{init}.md",
        f"{_REPORTS_DIR}/Technical-Review-{init}.md",
        f"{_REPORTS_DIR}/Implementation-Plan-{init}.md",
        f"{_REPORTS_DIR}/Pre-Implement-{init}-W*.md",
        f"{_REPORTS_DIR}/Wave-Execution-{init}-W*.md",
        f"{_REPORTS_DIR}/Live-Verify-{init}-W*.md",
        f"{_REPORTS_DIR}/Ground-Report-{init}-W*.md",
        f"{_REPORTS_DIR}/Learning-Extract-{init}-W*.md",
        f"{_ADR_DIR}/adr-*-*.md (Draft only)",
    ]
    planned_keep = [
        f"{_PRODUCT_SPEC_DIR}/{init}*.md",
        f"{_ADR_DIR}/ (Accepted ADRs only — refuse delete)",
        "src/ (source_roots — refuse delete)",
        "tests/unit/ (unit_tests_dir — refuse delete)",
        "tests/verify/ scripts (live_verify_dir — refuse delete)",
        ".harness/ (refuse delete)",
    ]
    return PurgePlanPreview(
        planned_delete=planned_delete,
        planned_keep=planned_keep,
        plan_source=PURGE_PLAN_SOURCE,
    )
