"""Initiative-closure start request/response models (ADR-010 §7 / INIT-GATEFLOW-010 W4)."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.models.dispatch_plan_models import DispatchPlan, NodeDispatchSpec
from src.models.pr_branch_naming import (
    build_closure_head_branch,
    validate_base_branch,
    validate_closure_branch_slug,
    validate_initiative_id,
)
from src.models.run_store_models import JobPayloadDocument

# Fixed Enter-at (ADR-010 §7 / pin initiative-closure graph). Client must not choose.
CLOSURE_START_NODE = "purge-initiative-artifacts-app"


class ClosureStartRequest(BaseModel):
    """POST /api/v1/initiatives/closure/start body (ADR-010 §7 initiative closure intake).

    Distinct from wave closeout (Pass-2): binds epic + wave ticket ids, not a wave PR.
    Enter-at is server-fixed to ``purge-initiative-artifacts-app``.
    """

    model_config = ConfigDict(extra="forbid")

    initiative_id: str = Field(description="Initiative id, e.g. INIT-GATEFLOW-010")
    epic_ticket_id: str = Field(description="EPIC board ticket id from create-tickets")
    wave_ticket_ids: list[str] = Field(
        description="Non-empty wave ticket ids from create-tickets (Done-gate input)",
        min_length=1,
    )
    workspace: str = Field(description="Absolute app workspace path for closure walk")
    branch_slug: str = Field(
        description="Lowercase kebab slug for initiative-closure head branch",
    )
    base_branch: str = Field(description="PR base branch (merge target)")
    runner: str = Field(description="AgentRunner adapter id for purge-initiative-artifacts-app")
    model_id: str = Field(description="Model id for purge-initiative-artifacts-app")
    node_dispatch: dict[str, NodeDispatchSpec] = Field(
        default_factory=dict,
        description="Optional per-node runner/model overrides; else inherit start defaults",
    )
    org: str
    repo: str

    @field_validator("initiative_id")
    @classmethod
    def _initiative_id(cls, value: str) -> str:
        return validate_initiative_id(value)

    @field_validator("branch_slug")
    @classmethod
    def _branch_slug(cls, value: str) -> str:
        return validate_closure_branch_slug(value)

    @field_validator("base_branch")
    @classmethod
    def _base_branch(cls, value: str) -> str:
        return validate_base_branch(value)

    @field_validator("epic_ticket_id", "runner", "model_id", "org", "repo", "workspace")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must be non-empty")
        return cleaned

    @field_validator("wave_ticket_ids")
    @classmethod
    def _wave_ticket_ids(cls, value: list[str]) -> list[str]:
        cleaned = [item.strip() for item in value if str(item).strip()]
        if not cleaned:
            raise ValueError("wave_ticket_ids must be a non-empty list of non-empty strings")
        return cleaned

    @model_validator(mode="after")
    def _require_absolute_workspace(self) -> "ClosureStartRequest":
        if not self.workspace.startswith("/"):
            raise ValueError("workspace must be an absolute path")
        return self

    def head_branch(self) -> str:
        """Deterministic closure PR head from validated identity fields."""
        return build_closure_head_branch(self.initiative_id, self.branch_slug)

    def build_dispatch_plan(self) -> DispatchPlan:
        """Build inherit-capable dispatch plan from start fields + node_dispatch."""
        return DispatchPlan(
            default=NodeDispatchSpec(runner=self.runner, model_id=self.model_id),
            nodes=dict(self.node_dispatch),
        )


class ClosureStartResponse(BaseModel):
    """Successful initiative-closure start accept response."""

    model_config = ConfigDict(extra="forbid")

    run_id: str
    job_id: Optional[str] = Field(default=None)
    status: str


class ClosureStartJobPayload(BaseModel):
    """Typed api_trigger job payload built at closure-start enqueue."""

    model_config = ConfigDict(extra="forbid")

    delivery_id: str
    event_type: str
    run_id: str
    org: str
    repo: str
    initiative_id: str
    ticket_id: str
    epic_ticket_id: str
    wave_ticket_ids: list[str]
    branch_slug: str
    base_branch: str
    start_node: str
    dispatch_plan: DispatchPlan
    handoff_path: str
    trigger_source: str = Field(default="api")
    issue_number: Optional[int] = Field(default=None)
    workspace_path: Optional[str] = Field(default=None)
    lane: str = Field(default="closure")
    head_ref: Optional[str] = Field(default=None)
    epic_done_applied: bool = Field(
        default=False,
        description="True when EPIC → Done was applied before enqueue (REQ-14 audit)",
    )

    def to_job_payload_document(self) -> JobPayloadDocument:
        """Map into RunStore JobPayloadDocument (extra keys allowed at store)."""
        return JobPayloadDocument.model_validate(self.model_dump(mode="json", exclude_none=True))
