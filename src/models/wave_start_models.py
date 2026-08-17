"""Lane-specific wave-start request/response models (ADR-010 / INIT-006 W3 + INIT-007)."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.models.dispatch_plan_models import DispatchPlan, NodeDispatchSpec
from src.models.pr_branch_naming import (
    build_spec_head_branch,
    build_wave_head_branch,
    normalize_wave_token,
    validate_base_branch,
    validate_branch_slug,
    validate_initiative_id,
)
from src.models.run_store_models import JobPayloadDocument

# Fixed Pass-2 Enter-at (ADR-010 §6 / INIT-GATEFLOW-007). Client must not choose.
CLOSEOUT_START_NODE = "learning-extract"
SPEC_DEFAULT_START_NODE = "spec-draft"
SPEC_DEFAULT_WAVE_ID = "W0"
SPEC_DEFAULT_BRANCH_SLUG = "spec"
IMPLEMENT_DEFAULT_BRANCH_SLUG = "implement"


class WaveStartTargetingFields(BaseModel):
    """Shared targeting + Enter-at fields (no workspace — lane-specific)."""

    model_config = ConfigDict(extra="forbid")

    initiative_id: str = Field(description="Initiative id, e.g. INIT-GATEFLOW-006")
    wave_id: str = Field(description="Wave id such as W0 / W1")
    branch_slug: str = Field(
        description="Lowercase kebab slug for the wave head branch",
    )
    base_branch: str = Field(description="PR base branch (merge target)")
    start_node: str = Field(
        description="Pin node id to Enter-at (must be skill + dispatch orchestrated)",
    )
    runner: str = Field(description="AgentRunner adapter id for start_node")
    model_id: str = Field(description="Model id for start_node")
    node_dispatch: dict[str, NodeDispatchSpec] = Field(
        default_factory=dict,
        description="Optional per-node runner/model overrides; else inherit start defaults",
    )
    org: str
    repo: str
    pr_number: Optional[int] = Field(default=None)
    issue_number: Optional[int] = Field(default=None)

    @field_validator("initiative_id")
    @classmethod
    def _initiative_id(cls, value: str) -> str:
        return validate_initiative_id(value)

    @field_validator("wave_id")
    @classmethod
    def _wave_id(cls, value: str) -> str:
        normalize_wave_token(value)
        return value.strip()

    @field_validator("branch_slug")
    @classmethod
    def _branch_slug(cls, value: str) -> str:
        return validate_branch_slug(value)

    @field_validator("base_branch")
    @classmethod
    def _base_branch(cls, value: str) -> str:
        return validate_base_branch(value)

    @field_validator("start_node")
    @classmethod
    def _start_node(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("start_node must be non-empty")
        return cleaned

    @field_validator("runner", "model_id")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must be non-empty")
        return cleaned

    def head_branch(self) -> str:
        """Deterministic PR head from validated identity fields."""
        return build_wave_head_branch(self.initiative_id, self.wave_id, self.branch_slug)

    def build_dispatch_plan(self) -> DispatchPlan:
        """Build inherit-capable dispatch plan from start fields + node_dispatch."""
        return DispatchPlan(
            default=NodeDispatchSpec(runner=self.runner, model_id=self.model_id),
            nodes=dict(self.node_dispatch),
        )


class ImplementWaveStartRequest(WaveStartTargetingFields):
    """POST /api/v1/waves/implement/start body (ADR-010 implement intake)."""

    ticket_id: str = Field(
        description="Forge ticket/issue id (required; must agree with initiative+wave)",
    )
    workspace_path: Optional[str] = Field(
        default=None,
        description="Optional app workspace path for implement lane",
    )
    force_harness_recheck: bool = Field(
        default=False,
        description="When true, ignore harness_verified cache and re-probe (REQ-22)",
    )

    @model_validator(mode="before")
    @classmethod
    def _default_branch_slug(cls, data: object) -> object:
        if isinstance(data, dict):
            raw = data.get("branch_slug")
            if raw is None or (isinstance(raw, str) and not raw.strip()):
                data = {**data, "branch_slug": IMPLEMENT_DEFAULT_BRANCH_SLUG}
        return data

    @field_validator("ticket_id")
    @classmethod
    def _ticket_id(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("ticket_id must be non-empty")
        return cleaned


class SpecWaveStartRequest(BaseModel):
    """POST /api/v1/waves/spec/start body (ADR-010 spec intake / INIT-019).

    Paths, ``start_node``, ``branch_slug``, ``initiative_id``, runner/model,
    and ``org``/``repo`` may be omitted; the service resolves them. App
    ``org``/``repo`` come from the programme's admitted fleet when omitted.
    """

    model_config = ConfigDict(extra="forbid")

    org: Optional[str] = Field(
        default=None,
        description="App org; derived from the single admitted fleet repo when omitted",
    )
    repo: Optional[str] = Field(
        default=None,
        description="App repo; derived from the single admitted fleet repo when omitted",
    )
    meta_pr_url: str = Field(
        description="prayog-meta (or programme) PR URL for accept-gate intake",
    )
    initiative_id: Optional[str] = Field(
        default=None,
        description="Optional; derived from the meta PR when omitted",
    )
    wave_id: str = Field(
        default=SPEC_DEFAULT_WAVE_ID,
        description="Wave id for ticket bind (default W0); ignored for spec head",
    )
    branch_slug: Optional[str] = Field(
        default=None,
        description="Ignored for spec head; payload default is spec when omitted",
    )
    base_branch: str = Field(description="PR base branch (merge target)")
    start_node: Optional[str] = Field(
        default=None,
        description="Optional Enter-at; pin default spec-draft when omitted",
    )
    runner: Optional[str] = Field(
        default=None,
        description="Optional; lane_defaults[spec] when omitted",
    )
    model_id: Optional[str] = Field(
        default=None,
        description="Optional; lane_defaults[spec] when omitted",
    )
    node_dispatch: dict[str, NodeDispatchSpec] = Field(
        default_factory=dict,
        description="Optional per-node runner/model overrides; else inherit start defaults",
    )
    workspace_path: Optional[str] = Field(
        default=None,
        description="Optional absolute app workspace; resolved when omitted",
    )
    meta_workspace_path: Optional[str] = Field(
        default=None,
        description="Optional absolute meta checkout; resolved when omitted",
    )
    ticket_id: Optional[str] = Field(
        default=None,
        description="Optional ticket; defaults to initiative:wave for bind",
    )
    pr_number: Optional[int] = Field(default=None)
    issue_number: Optional[int] = Field(default=None)

    @field_validator("org", "repo")
    @classmethod
    def _optional_org_repo(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    @field_validator("meta_pr_url")
    @classmethod
    def _required_non_empty(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must be non-empty")
        return cleaned

    @field_validator("initiative_id")
    @classmethod
    def _initiative_id(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            return None
        return validate_initiative_id(cleaned)

    @field_validator("wave_id")
    @classmethod
    def _wave_id(cls, value: str) -> str:
        normalize_wave_token(value)
        return value.strip()

    @field_validator("branch_slug")
    @classmethod
    def _branch_slug(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            return None
        return validate_branch_slug(cleaned)

    @field_validator("start_node", "runner", "model_id")
    @classmethod
    def _optional_non_empty(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            return None
        return cleaned

    @field_validator("workspace_path", "meta_workspace_path")
    @classmethod
    def _optional_absolute_path(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            return None
        if not cleaned.startswith("/"):
            raise ValueError("must be an absolute path")
        return cleaned

    @field_validator("base_branch")
    @classmethod
    def _base_branch(cls, value: str) -> str:
        return validate_base_branch(value)

    def head_branch(self, initiative_id: str) -> str:
        """Spec Draft PR head — initiative only; wave_id/branch_slug ignored for head."""
        return build_spec_head_branch(initiative_id)

    def as_targeting_fields(
        self,
        *,
        initiative_id: str,
        wave_id: str,
        branch_slug: str,
        start_node: str,
        runner: str,
        model_id: str,
        org: str,
        repo: str,
    ) -> WaveStartTargetingFields:
        """Project resolved spec defaults into shared targeting for enqueue."""
        return WaveStartTargetingFields(
            initiative_id=initiative_id,
            wave_id=wave_id,
            branch_slug=branch_slug,
            base_branch=self.base_branch,
            start_node=start_node,
            runner=runner,
            model_id=model_id,
            node_dispatch=dict(self.node_dispatch),
            org=org,
            repo=repo,
            pr_number=self.pr_number,
            issue_number=self.issue_number,
        )


class CloseoutWaveStartRequest(BaseModel):
    """POST /api/v1/waves/closeout/start body (ADR-010 §6 Pass-2 intake).

    Enter-at is server-fixed to ``learning-extract`` — no client ``start_node``.
    Meta intake fields are forbidden. ``pr_number`` and absolute workspace required.

    Publish head is resolved from the open wave PR (``pr_number``), not from
    ``branch_slug``. Optional ``branch_slug`` is non-binding (ignored for head).
    """

    model_config = ConfigDict(extra="forbid")

    initiative_id: str = Field(description="Initiative id, e.g. INIT-GATEFLOW-007")
    wave_id: str = Field(description="Wave id such as W0 / W1")
    ticket_id: str = Field(
        description="Forge ticket/issue id (required; must agree with initiative+wave)",
    )
    branch_slug: Optional[str] = Field(
        default=None,
        description=(
            "Optional; ignored for publish head. Closeout binds head from pr_number. "
            "Kept for backward-compatible clients."
        ),
    )
    base_branch: str = Field(description="PR base branch (merge target)")
    runner: str = Field(description="AgentRunner adapter id for learning-extract")
    model_id: str = Field(description="Model id for learning-extract")
    node_dispatch: dict[str, NodeDispatchSpec] = Field(
        default_factory=dict,
        description="Optional per-node runner/model overrides; else inherit start defaults",
    )
    org: str
    repo: str
    pr_number: int = Field(
        description="Existing wave PR number — SSOT for Pass-2 publish head",
    )
    workspace_path: str = Field(
        description="Absolute app workspace path checked out on the wave PR tip",
    )
    issue_number: Optional[int] = Field(default=None)
    prior_run_id: Optional[UUID] = Field(
        default=None,
        description="Optional audit link to Pass-1 run; does not resume walker state",
    )

    @field_validator("initiative_id")
    @classmethod
    def _initiative_id(cls, value: str) -> str:
        return validate_initiative_id(value)

    @field_validator("wave_id")
    @classmethod
    def _wave_id(cls, value: str) -> str:
        normalize_wave_token(value)
        return value.strip()

    @field_validator("branch_slug")
    @classmethod
    def _branch_slug(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            return None
        return validate_branch_slug(cleaned)

    @field_validator("base_branch")
    @classmethod
    def _base_branch(cls, value: str) -> str:
        return validate_base_branch(value)

    @field_validator("ticket_id", "runner", "model_id", "org", "repo", "workspace_path")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must be non-empty")
        return cleaned

    @field_validator("pr_number")
    @classmethod
    def _pr_number(cls, value: int) -> int:
        if value < 1:
            raise ValueError("pr_number must be a positive integer")
        return value

    @model_validator(mode="after")
    def _require_absolute_workspace(self) -> "CloseoutWaveStartRequest":
        if not self.workspace_path.startswith("/"):
            raise ValueError("workspace_path must be an absolute path")
        return self

    def build_dispatch_plan(self) -> DispatchPlan:
        """Build inherit-capable dispatch plan from start fields + node_dispatch."""
        return DispatchPlan(
            default=NodeDispatchSpec(runner=self.runner, model_id=self.model_id),
            nodes=dict(self.node_dispatch),
        )

    def as_targeting_fields(self, *, branch_slug: str) -> WaveStartTargetingFields:
        """Project into shared targeting with fixed closeout Enter-at.

        ``branch_slug`` must already be resolved for job payload compatibility
        (derived from PR head when the client omitted it).
        """
        return WaveStartTargetingFields(
            initiative_id=self.initiative_id,
            wave_id=self.wave_id,
            branch_slug=branch_slug,
            base_branch=self.base_branch,
            start_node=CLOSEOUT_START_NODE,
            runner=self.runner,
            model_id=self.model_id,
            node_dispatch=dict(self.node_dispatch),
            org=self.org,
            repo=self.repo,
            pr_number=self.pr_number,
            issue_number=self.issue_number,
        )


class WaveStartResponse(BaseModel):
    """Successful wave-start accept response (shared)."""

    model_config = ConfigDict(extra="forbid")

    run_id: str
    job_id: Optional[str] = Field(default=None)
    status: str


class WaveStartJobPayload(BaseModel):
    """Typed api_trigger job payload built at wave-start enqueue (S1)."""

    model_config = ConfigDict(extra="forbid")

    delivery_id: str
    event_type: str
    run_id: str
    org: str
    repo: str
    initiative_id: str
    wave_id: str
    ticket_id: str
    branch_slug: str
    base_branch: str
    start_node: str
    dispatch_plan: DispatchPlan
    handoff_path: str
    trigger_source: str = Field(default="api")
    pr_number: Optional[int] = Field(default=None)
    issue_number: Optional[int] = Field(default=None)
    workspace_path: Optional[str] = Field(default=None)
    meta_pr_url: Optional[str] = Field(default=None)
    meta_head_sha: Optional[str] = Field(default=None)
    meta_workspace_path: Optional[str] = Field(default=None)
    prior_run_id: Optional[str] = Field(
        default=None,
        description="Optional Pass-1 run id audit link (closeout only)",
    )
    lane: Optional[str] = Field(
        default=None,
        description="Lane id: implement | spec | closeout (head naming / orch)",
    )
    head_ref: Optional[str] = Field(
        default=None,
        description=(
            "Resolved publish head (closeout: open wave PR head.ref; "
            "spec: feature/{INIT}-spec). "
            "When set, orchestrator must not invent head from branch_slug."
        ),
    )
    force_harness_recheck: bool = Field(
        default=False,
        description="When true, orchestrator ignores harness_verified cache (REQ-22)",
    )

    def to_job_payload_document(self) -> JobPayloadDocument:
        """Map into RunStore JobPayloadDocument (extra keys allowed at store)."""
        return JobPayloadDocument.model_validate(self.model_dump(mode="json", exclude_none=True))
