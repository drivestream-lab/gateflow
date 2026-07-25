"""Unit tests for HandoffReader and WorkflowEngine."""

from pathlib import Path

import pytest

from src.business_services.handoff_reader import HandoffReader
from src.business_services.workflow_engine import WorkflowEngine
from src.models.handoff_models import HandoffEnvelope


def test_parse_and_find_handoff(tmp_path: Path) -> None:
    reports = tmp_path / "docs" / "specification" / "reports"
    reports.mkdir(parents=True)
    (reports / "sample.md").write_text(
        "# Sample\n\n```yaml\nhandoff:\n  contract: sdd-delivery/v2\n"
        "  stage: board-seed\n  outcome: pass\n  blockers: []\n"
        "  signals: {}\n  next_candidates:\n    - pre-implement\n"
        "  human_checkpoint: false\n  external_action: false\n```\n",
        encoding="utf-8",
    )
    reader = HandoffReader()
    envelope = reader.find_latest_handoff(tmp_path)
    assert envelope.stage == "board-seed"
    assert envelope.outcome == "pass"


def test_workflow_resolve_next_from_pin() -> None:
    engine = WorkflowEngine()
    engine.load_pin()
    handoff = HandoffEnvelope(
        contract="sdd-delivery/v2",
        stage="board-seed",
        outcome="pass",
    )
    resolved = engine.resolve_next(handoff)
    assert resolved.node_id == "pre-implement"
    assert resolved.node_type == "skill"
    # board-seed is manual in pin; next node pre-implement is orchestrated
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
        engine.require_orchestrated_skill("board-seed")


def test_workflow_missing_pin_fails(tmp_path: Path) -> None:
    engine = WorkflowEngine()
    with pytest.raises(FileNotFoundError):
        engine.load_pin(workflow_path=tmp_path / "missing.yaml")
