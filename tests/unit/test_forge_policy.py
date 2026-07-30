"""Unit tests for pin forge parse and WorkflowEngine forge policy."""

import pytest

from src.business_services.workflow_engine import WorkflowEngine
from src.models.forge_models import HandoffForgeDocument, parse_node_forge
from src.models.forge_types import (
    AuthorizationModeType,
    CommitWorkspaceModeType,
    ForgeActionType,
)
from src.models.handoff_models import HandoffEnvelope


def test_parse_node_forge_absent_defaults_disabled() -> None:
    policy = parse_node_forge(None)
    assert policy.commit_workspace == CommitWorkspaceModeType.DISABLED
    assert policy.action is None


def test_parse_node_forge_commit_workspace_modes() -> None:
    for mode in CommitWorkspaceModeType:
        policy = parse_node_forge({"commit_workspace": mode.value})
        assert policy.commit_workspace == mode


def test_parse_node_forge_invalid_mode_fails_closed() -> None:
    with pytest.raises(ValueError, match="commit_workspace"):
        parse_node_forge({"commit_workspace": "maybe"})


def test_parse_node_forge_forbids_lgtm_apply_labels() -> None:
    with pytest.raises(ValueError, match="lgtm"):
        parse_node_forge(
            {
                "action": "open_draft_pr",
                "apply_labels": ["impact-map-lgtm"],
            }
        )


def test_parse_node_forge_external_action() -> None:
    policy = parse_node_forge(
        {
            "action": "open_draft_pr",
            "draft": True,
            "apply_labels": ["impact-map-pending"],
            "requires": ["title", "body_path"],
        }
    )
    assert policy.action == ForgeActionType.OPEN_DRAFT_PR
    assert policy.draft is True
    assert policy.apply_labels == ["impact-map-pending"]
    assert policy.requires == ["title", "body_path"]


def test_handoff_envelope_parses_forge_document() -> None:
    envelope = HandoffEnvelope(
        contract="sdd-delivery/v2",
        stage="prd-impact-map",
        outcome="pass",
        forge=HandoffForgeDocument.model_validate(
            {
                "action": "open_draft_pr",
                "title": "Draft impact map",
                "body_path": "docs/pr-body.md",
            }
        ),
    )
    assert envelope.forge is not None
    assert envelope.forge.action == "open_draft_pr"
    assert envelope.forge.title == "Draft impact map"


def test_pin_matrix_implement_lane_commit_workspace() -> None:
    engine = WorkflowEngine()
    engine.load_pin()
    assert (
        engine.get_node("pre-implement").forge.commit_workspace == CommitWorkspaceModeType.REQUIRED
    )
    assert engine.get_node("loop-spec").forge.commit_workspace == CommitWorkspaceModeType.REQUIRED
    assert engine.get_node("verify").forge.commit_workspace == CommitWorkspaceModeType.OPTIONAL
    assert engine.get_node("ground-spec").forge.commit_workspace == CommitWorkspaceModeType.REQUIRED


def test_pin_external_action_authorization_day_one_matrix() -> None:
    engine = WorkflowEngine()
    engine.load_pin()
    assert engine.get_node("wave-pr-action").authorization == AuthorizationModeType.AUTOMATED
    assert engine.get_node("spec-pr-action").authorization == AuthorizationModeType.AUTOMATED
    assert engine.get_node("prd-pr-action").authorization == AuthorizationModeType.EXPLICIT
    assert engine.get_node("board-tickets-action").authorization == AuthorizationModeType.EXPLICIT
    assert engine.get_node("pre-implement").authorization is None


def test_external_action_missing_authorization_fails_closed() -> None:
    with pytest.raises(ValueError, match="missing required authorization"):
        WorkflowEngine._to_resolved(
            "bad-ea",
            {
                "type": "external-action",
                "forge": {"action": "open_draft_pr", "draft": True, "requires": ["title"]},
            },
        )


def test_external_action_unknown_authorization_fails_closed() -> None:
    with pytest.raises(ValueError, match="unknown authorization"):
        WorkflowEngine._to_resolved(
            "bad-ea",
            {
                "type": "external-action",
                "authorization": "maybe",
                "forge": {"action": "open_draft_pr", "draft": True, "requires": ["title"]},
            },
        )


def test_pin_external_action_open_draft_pr() -> None:
    engine = WorkflowEngine()
    engine.load_pin()
    node = engine.get_node("prd-pr-action")
    assert node.node_type == "external-action"
    assert node.forge.action == ForgeActionType.OPEN_DRAFT_PR
    assert node.forge.draft is True
    assert "impact-map-pending" in node.forge.apply_labels
    assert "title" in node.forge.requires


def test_resolve_next_carries_forge_from_pin() -> None:
    engine = WorkflowEngine()
    engine.load_pin()
    handoff = HandoffEnvelope(
        contract="sdd-delivery/v2",
        stage="pre-implement",
        outcome="pass",
    )
    resolved = engine.resolve_next(handoff)
    assert resolved.node_id == "loop-spec"
    assert resolved.forge.commit_workspace == CommitWorkspaceModeType.REQUIRED
