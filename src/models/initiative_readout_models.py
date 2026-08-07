"""Initiative read-out DTOs (INIT-GATEFLOW-011 CAP-03 / W2 — Gateflow-owned).

REQ-09: initiative list/detail returns id, name, PRD approval state, affected
repos, current stage, and link to any in-flight run — fields present or
explicitly ``unavailable``. REQ-10: composed only from Gateflow-owned data
(runs, board tickets) plus at most one read-only meta PR/label read (W3).
W2 wires no meta read, so ``prd_approval`` is always ``unavailable`` here.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class InitiativeStageType(str, Enum):
    """Plain-language current stage for an initiative (derived from run + board state)."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    WAITING = "waiting"
    DONE = "done"
    UNKNOWN = "unknown"


class PrdApprovalStateType(str, Enum):
    """PRD approval state for an initiative (CAP-01 against ``prd-impact-acceptance``)."""

    SATISFIED = "satisfied"
    NOT_SATISFIED = "not_satisfied"
    COULD_NOT_VERIFY = "could_not_verify"
    UNAVAILABLE = "unavailable"


class InitiativeRunLink(BaseModel):
    """Link to an in-flight (active) run for an initiative."""

    model_config = ConfigDict(extra="forbid")

    run_id: str
    wave_id: Optional[str] = Field(default=None)
    status_type: str = Field(
        description="Run lifecycle status: active | stopped | failed | completed"
    )
    workflow_node: Optional[str] = Field(default=None)
    pr_number: Optional[int] = Field(default=None)
    org: str
    repo: str


class InitiativeListItem(BaseModel):
    """One row in the initiative list (Gateflow-owned fields only)."""

    model_config = ConfigDict(extra="forbid")

    initiative_id: str
    name: str = Field(description="EPIC ticket title when known, else the initiative id")
    prd_approval: PrdApprovalStateType = Field(
        description="CAP-01 against prd-impact-acceptance; unavailable until W3 meta bridge"
    )
    prd_approval_reason: Optional[str] = Field(
        default=None,
        description="Why prd_approval is unavailable / could_not_verify (plain language)",
    )
    affected_repos: list[str] = Field(
        default_factory=list,
        description="Distinct 'org/repo' pairs touched by runs for this initiative",
    )
    current_stage: InitiativeStageType
    current_stage_detail: Optional[str] = Field(
        default=None,
        description="Plain-language detail for the current stage (wave id, node, reason)",
    )
    in_flight_run: Optional[InitiativeRunLink] = Field(
        default=None,
        description="Active run link when an in-flight run exists, else None",
    )
    epic_ticket_id: Optional[str] = Field(default=None)
    epic_ticket_url: Optional[str] = Field(default=None)


class InitiativeReadout(InitiativeListItem):
    """Initiative detail — same fields as the list item (W2 Gateflow-owned only).

    W3 extends this with meta-derived ``prd_approval`` population. The shape is
    intentionally identical to the list item so list and detail compose the
    same Gateflow-owned fields; detail may carry extra optional fields later.
    """

    model_config = ConfigDict(extra="forbid")


class InitiativeListResult(BaseModel):
    """GET /api/v1/initiatives response wrapper."""

    model_config = ConfigDict(extra="forbid")

    initiatives: list[InitiativeListItem] = Field(default_factory=list)
