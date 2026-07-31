"""Unit tests for HandoffReader and WorkflowEngine."""

from pathlib import Path

import pytest

from src.business_services.handoff_reader import HandoffReader
from src.business_services.workflow_engine import WorkflowEngine
from src.models.forge_types import AuthorizationModeType
from src.models.handoff_models import HandoffEnvelope


_HANDOFF_BODY = (
    "handoff:\n  contract: sdd-delivery/v2\n"
    "  stage: pre-implement\n  outcome: pass\n  blockers: []\n"
    "  signals: {}\n  next_candidates:\n    - loop-spec\n"
    "  human_checkpoint: false\n  external_action: false\n"
)


def test_read_path_parses_stored_baton(tmp_path: Path) -> None:
    baton = tmp_path / "run-a" / "handoff.md"
    baton.parent.mkdir(parents=True)
    baton.write_text(f"```yaml\n{_HANDOFF_BODY}```\n", encoding="utf-8")
    reader = HandoffReader()
    envelope = reader.read_path(baton)
    assert envelope.stage == "pre-implement"
    assert envelope.outcome == "pass"


def test_read_path_plain_yaml_without_fence(tmp_path: Path) -> None:
    baton = tmp_path / "handoff.md"
    baton.write_text(_HANDOFF_BODY, encoding="utf-8")
    envelope = HandoffReader().read_path(str(baton))
    assert envelope.stage == "pre-implement"


def test_read_path_missing_fails_closed(tmp_path: Path) -> None:
    missing = tmp_path / "missing" / "handoff.md"
    with pytest.raises(ValueError, match="missing or not a file"):
        HandoffReader().read_path(missing)


def test_read_path_empty_string_fails_closed() -> None:
    with pytest.raises(ValueError, match="handoff_path is empty"):
        HandoffReader().read_path("   ")


def test_read_path_empty_file_fails_closed(tmp_path: Path) -> None:
    baton = tmp_path / "handoff.md"
    baton.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="No handoff YAML block"):
        HandoffReader().read_path(baton)


def _write_baton(path: Path, *, stage: str, outcome: str = "pass") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = (
        "handoff:\n  contract: sdd-delivery/v2\n"
        f"  stage: {stage}\n  outcome: {outcome}\n  blockers: []\n"
        "  signals: {}\n  next_candidates: []\n"
        "  human_checkpoint: false\n  external_action: false\n"
    )
    path.write_text(body, encoding="utf-8")


def test_dual_run_isolation_distinct_handoff_paths(tmp_path: Path) -> None:
    """REQ-8b: two runs sharing a workspace tree never cross-ingest via stored paths."""
    workspace = tmp_path / "workspace"
    reports = workspace / "docs" / "specification" / "reports"
    reports.mkdir(parents=True)
    # Workspace decoy must not be used — ingest is stored-path only (ADR-008).
    (reports / "ambient-decoy.md").write_text(
        "# decoy\n\n```yaml\n"
        "handoff:\n  contract: sdd-delivery/v2\n"
        "  stage: ambient-decoy\n  outcome: pass\n  blockers: []\n"
        "  signals: {}\n  next_candidates: []\n"
        "  human_checkpoint: false\n  external_action: false\n"
        "```\n",
        encoding="utf-8",
    )

    handoff_root = tmp_path / "GATEFLOW_HANDOFF_ROOT"
    baton_a = handoff_root / "run-aaa" / "handoff.md"
    baton_b = handoff_root / "run-bbb" / "handoff.md"
    _write_baton(baton_a, stage="pre-implement")
    _write_baton(baton_b, stage="loop-spec")

    reader = HandoffReader()
    env_a = reader.read_path(baton_a)
    env_b = reader.read_path(baton_b)
    assert env_a.stage == "pre-implement"
    assert env_b.stage == "loop-spec"
    assert env_a.stage != env_b.stage
    assert "ambient-decoy" not in {env_a.stage, env_b.stage}
    assert workspace.is_dir()  # shared tree present; unused by read_path


def test_workflow_resolve_next_from_pin() -> None:
    engine = WorkflowEngine()
    engine.load_pin()
    handoff = HandoffEnvelope(
        contract="sdd-delivery/v2",
        stage="pre-implement",
        outcome="pass",
    )
    resolved = engine.resolve_next(handoff)
    assert resolved.node_id == "loop-spec"
    assert resolved.node_type == "skill"
    assert resolved.dispatch == "orchestrated"


def test_require_orchestrated_skill_ok() -> None:
    engine = WorkflowEngine()
    engine.load_pin()
    node = engine.require_orchestrated_skill("loop-spec")
    assert node.node_id == "loop-spec"
    assert node.dispatch == "orchestrated"


def test_require_orchestrated_skill_rejects_manual() -> None:
    engine = WorkflowEngine()
    engine.load_pin()
    with pytest.raises(ValueError, match="orchestrated"):
        engine.require_orchestrated_skill("validate-requirements")


def test_loop_spec_pass_resolves_to_wave_pr_action() -> None:
    """Pass-1 pin: loop-spec pass → wave-pr-action (external-action, automated)."""
    engine = WorkflowEngine()
    engine.load_pin()
    handoff = HandoffEnvelope(
        contract="sdd-delivery/v2",
        stage="loop-spec",
        outcome="pass",
    )
    resolved = engine.resolve_next(handoff)
    assert resolved.node_id == "wave-pr-action"
    assert resolved.node_type == "external-action"
    assert resolved.authorization == AuthorizationModeType.AUTOMATED


def test_verify_is_manual_learning_extract_and_ground_are_orchestrated() -> None:
    """Closeout pin: verify manual; learning-extract → ground-spec orchestrated."""
    engine = WorkflowEngine()
    engine.load_pin()
    assert engine.get_node("verify").dispatch == "manual"
    assert engine.get_node("learning-extract").dispatch == "orchestrated"
    assert engine.get_node("ground-spec").dispatch == "orchestrated"
    with pytest.raises(ValueError, match="orchestrated"):
        engine.require_orchestrated_skill("verify")
    assert engine.require_orchestrated_skill("learning-extract").node_id == "learning-extract"
    handoff = HandoffEnvelope(
        contract="sdd-delivery/v2",
        stage="learning-extract",
        outcome="pass",
    )
    assert engine.resolve_next(handoff).node_id == "ground-spec"
    ground_pass = HandoffEnvelope(
        contract="sdd-delivery/v2",
        stage="ground-spec",
        outcome="pass",
    )
    assert engine.resolve_next(ground_pass).node_id == "wave-signoff"
    assert engine.get_node("wave-signoff").node_type == "human-checkpoint"


def test_workflow_missing_pin_fails(tmp_path: Path) -> None:
    engine = WorkflowEngine()
    with pytest.raises(FileNotFoundError):
        engine.load_pin(workflow_path=tmp_path / "missing.yaml")
