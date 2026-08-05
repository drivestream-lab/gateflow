"""Forge pin policy and handoff instance payloads (sdd-delivery/v2)."""

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from src.models.forge_types import (
    BoardStatusType,
    CommitWorkspaceModeType,
    ForgeActionType,
)


class NodeForgePolicy(BaseModel):
    """Parsed ``forge:`` block from a workflow.yaml node."""

    model_config = ConfigDict(extra="ignore")

    commit_workspace: CommitWorkspaceModeType = Field(
        default=CommitWorkspaceModeType.DISABLED,
        description="Skill-node publish policy; absent pin field → disabled",
    )
    action: Optional[ForgeActionType] = Field(
        default=None,
        description="External-action forge.action when present",
    )
    status: Optional[BoardStatusType] = Field(
        default=None,
        description="Board column target when action is update_board_status",
    )
    draft: Optional[bool] = Field(default=None)
    apply_labels: list[str] = Field(default_factory=list)
    remove_labels: list[str] = Field(default_factory=list)
    requires: list[str] = Field(default_factory=list)


class HandoffForgeDocument(BaseModel):
    """Optional ``handoff.forge`` instance payload (pin wins on policy fields)."""

    model_config = ConfigDict(extra="allow")

    action: Optional[str] = Field(default=None)
    draft: Optional[bool] = Field(default=None)
    apply_labels: Optional[list[str]] = Field(default=None)
    remove_labels: Optional[list[str]] = Field(default=None)
    title: Optional[str] = Field(default=None)
    body_path: Optional[str] = Field(default=None)
    initiative: Optional[str] = Field(default=None)
    plan_path: Optional[str] = Field(default=None)
    project_number: Optional[int] = Field(
        default=None,
        description="Org Project v2 number for create_board_tickets (caller-supplied)",
    )
    project_owner: Optional[str] = Field(
        default=None,
        description="Project owner org; defaults to run org when omitted",
    )
    head_ref: Optional[str] = Field(
        default=None,
        description="PR head branch when listed in pin forge.requires",
    )
    base_ref: Optional[str] = Field(
        default=None,
        description="PR base branch when listed in pin forge.requires",
    )


class CommitPathsResult(BaseModel):
    """Result of ForgeClient.commit_paths_to_branch."""

    model_config = ConfigDict(extra="forbid")

    commit_sha: str
    branch: str
    path_count: int
    paths: list[str] = Field(default_factory=list)


class EffectiveForgePolicy(BaseModel):
    """Pin policy ⋉ handoff instance slots ready for ForgeClient / BoardService."""

    model_config = ConfigDict(extra="forbid")

    action: ForgeActionType
    draft: bool = Field(default=True)
    apply_labels: list[str] = Field(default_factory=list)
    remove_labels: list[str] = Field(default_factory=list)
    title: Optional[str] = Field(default=None)
    body_path: Optional[str] = Field(default=None)
    initiative: Optional[str] = Field(default=None)
    plan_path: Optional[str] = Field(default=None)
    project_number: Optional[int] = Field(default=None)
    project_owner: Optional[str] = Field(default=None)
    head_ref: Optional[str] = Field(default=None)
    base_ref: Optional[str] = Field(default=None)


class OpenDraftPrResult(BaseModel):
    """Result of open_draft_pr forge action."""

    model_config = ConfigDict(extra="forbid")

    pr_number: int
    draft: bool
    applied_labels: list[str] = Field(default_factory=list)
    removed_labels: list[str] = Field(default_factory=list)


class BoardTicketsSeedResult(BaseModel):
    """Result of create_board_tickets forge action."""

    model_config = ConfigDict(extra="forbid")

    initiative: str
    epic_ticket_id: Optional[str] = Field(default=None)
    wave_ticket_ids: list[str] = Field(default_factory=list)
    created_count: int = Field(default=0)
    replayed_count: int = Field(default=0)


class ForgeAuthorizeRequest(BaseModel):
    """POST /api/v1/runs/{run_id}/forge/authorize — explicit mutate gate."""

    model_config = ConfigDict(extra="forbid")

    authorized: bool = Field(description="Must be true to execute pending external-action forge")
    workspace_path: str = Field(description="Workspace root for body_path / plan_path resolution")
    head: Optional[str] = Field(
        default=None,
        description="PR head branch for open_draft_pr (required for that action)",
    )
    base: Optional[str] = Field(
        default=None,
        description="PR base branch for open_draft_pr (required for that action)",
    )
    project_number: Optional[int] = Field(
        default=None,
        description=(
            "Org Project v2 number for create_board_tickets "
            "(overrides handoff.forge.project_number when set)"
        ),
        gt=0,
    )
    project_owner: Optional[str] = Field(
        default=None,
        description="Project owner org for create_board_tickets (defaults to run org)",
    )


class ForgeAuthorizeResponse(BaseModel):
    """Authorize + execute response."""

    model_config = ConfigDict(extra="forbid")

    run_id: str
    workflow_node: str
    action: ForgeActionType
    pr_number: Optional[int] = Field(default=None)
    board: Optional[BoardTicketsSeedResult] = Field(default=None)


def merge_pin_and_handoff_forge(
    pin: NodeForgePolicy,
    handoff_forge: Optional[HandoffForgeDocument],
) -> EffectiveForgePolicy:
    """Merge pin policy with handoff instance slots. Pin wins; conflicts fail closed."""
    if pin.action is None:
        raise ValueError("pin forge.action is required to merge external-action forge")

    hf = handoff_forge or HandoffForgeDocument()

    if hf.action is not None and str(hf.action) != pin.action.value:
        raise ValueError(
            f"handoff.forge.action {hf.action!r} conflicts with pin action {pin.action.value!r}"
        )

    if hf.draft is not None and pin.draft is not None and hf.draft != pin.draft:
        raise ValueError(f"handoff.forge.draft {hf.draft!r} conflicts with pin draft {pin.draft!r}")

    if hf.apply_labels:
        for label in hf.apply_labels:
            if label.endswith("-lgtm"):
                raise ValueError(f"handoff.forge.apply_labels forbids approval label {label!r}")
            if label not in pin.apply_labels:
                raise ValueError(f"handoff.forge.apply_labels invents {label!r} outside pin policy")

    if hf.remove_labels:
        for label in hf.remove_labels:
            if label not in pin.remove_labels:
                raise ValueError(
                    f"handoff.forge.remove_labels invents {label!r} outside pin policy"
                )

    slots: dict[str, Optional[str]] = {
        "title": hf.title,
        "body_path": hf.body_path,
        "initiative": hf.initiative,
        "plan_path": hf.plan_path,
        "head_ref": hf.head_ref,
        "base_ref": hf.base_ref,
    }
    missing = [
        name
        for name in pin.requires
        if not (slots.get(name) is not None and str(slots[name]).strip())
    ]
    if missing:
        raise ValueError(f"Incomplete handoff.forge; missing required slots: {missing}")

    draft = pin.draft if pin.draft is not None else True
    return EffectiveForgePolicy(
        action=pin.action,
        draft=draft,
        apply_labels=list(pin.apply_labels),
        remove_labels=list(pin.remove_labels),
        title=hf.title.strip() if hf.title else None,
        body_path=hf.body_path.strip() if hf.body_path else None,
        initiative=hf.initiative.strip() if hf.initiative else None,
        plan_path=hf.plan_path.strip() if hf.plan_path else None,
        project_number=hf.project_number if hf.project_number and hf.project_number > 0 else None,
        project_owner=hf.project_owner.strip() if hf.project_owner else None,
        head_ref=hf.head_ref.strip() if hf.head_ref else None,
        base_ref=hf.base_ref.strip() if hf.base_ref else None,
    )


def parse_node_forge(raw: Any) -> NodeForgePolicy:
    """Parse a workflow node ``forge`` mapping; fail closed on invalid enums."""
    if raw is None:
        return NodeForgePolicy()
    if not isinstance(raw, dict):
        raise ValueError(f"forge must be a mapping, got {type(raw).__name__}")

    cw_raw = raw.get("commit_workspace")
    if cw_raw is None:
        commit_workspace = CommitWorkspaceModeType.DISABLED
    else:
        try:
            commit_workspace = CommitWorkspaceModeType(str(cw_raw))
        except ValueError as exc:
            raise ValueError(
                f"Invalid forge.commit_workspace {cw_raw!r}; "
                f"expected {[m.value for m in CommitWorkspaceModeType]}"
            ) from exc

    action: Optional[ForgeActionType] = None
    if "action" in raw and raw.get("action") is not None:
        try:
            action = ForgeActionType(str(raw["action"]))
        except ValueError as exc:
            raise ValueError(
                f"Invalid forge.action {raw.get('action')!r}; "
                f"expected {[a.value for a in ForgeActionType]}"
            ) from exc

    apply_labels = raw.get("apply_labels") or []
    remove_labels = raw.get("remove_labels") or []
    requires = raw.get("requires") or []
    if not isinstance(apply_labels, list) or not all(isinstance(x, str) for x in apply_labels):
        raise ValueError("forge.apply_labels must be a list of strings")
    if not isinstance(remove_labels, list) or not all(isinstance(x, str) for x in remove_labels):
        raise ValueError("forge.remove_labels must be a list of strings")
    if not isinstance(requires, list) or not all(isinstance(x, str) for x in requires):
        raise ValueError("forge.requires must be a list of strings")

    for label in apply_labels:
        if label.endswith("-lgtm"):
            raise ValueError(f"forge.apply_labels forbids approval label {label!r}")

    draft = raw.get("draft")
    if draft is not None and not isinstance(draft, bool):
        raise ValueError("forge.draft must be a boolean when set")

    status: Optional[BoardStatusType] = None
    if "status" in raw and raw.get("status") is not None:
        try:
            status = BoardStatusType(str(raw["status"]))
        except ValueError as exc:
            raise ValueError(
                f"Invalid forge.status {raw.get('status')!r}; "
                f"expected {[s.value for s in BoardStatusType]}"
            ) from exc

    if action == ForgeActionType.UPDATE_BOARD_STATUS and status is None:
        raise ValueError(
            "forge.status is required when forge.action is update_board_status "
            f"(expected {[s.value for s in BoardStatusType]})"
        )

    return NodeForgePolicy(
        commit_workspace=commit_workspace,
        action=action,
        status=status,
        draft=draft if isinstance(draft, bool) else None,
        apply_labels=[str(x) for x in apply_labels],
        remove_labels=[str(x) for x in remove_labels],
        requires=[str(x) for x in requires],
    )
