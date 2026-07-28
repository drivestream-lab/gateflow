"""Unit tests for HandoffReader and WorkflowEngine."""

from pathlib import Path

import pytest

from src.business_services.handoff_reader import HandoffReader
from src.business_services.workflow_engine import WorkflowEngine
from src.models.handoff_models import HandoffEnvelope


_HANDOFF_BODY = (
    "handoff:\n  contract: sdd-delivery/v2\n"
    "  stage: board-seed\n  outcome: pass\n  blockers: []\n"
    "  signals: {}\n  next_candidates:\n    - pre-implement\n"
    "  human_checkpoint: false\n  external_action: false\n"
)


def test_parse_and_find_handoff(tmp_path: Path) -> None:
    reports = tmp_path / "docs" / "specification" / "reports"
    reports.mkdir(parents=True)
    (reports / "sample.md").write_text(
        f"# Sample\n\n```yaml\n{_HANDOFF_BODY}```\n",
        encoding="utf-8",
    )
    reader = HandoffReader()
    envelope = reader.find_latest_handoff(tmp_path)
    assert envelope.stage == "board-seed"
    assert envelope.outcome == "pass"


def test_read_path_parses_stored_baton(tmp_path: Path) -> None:
    baton = tmp_path / "run-a" / "handoff.md"
    baton.parent.mkdir(parents=True)
    baton.write_text(f"```yaml\n{_HANDOFF_BODY}```\n", encoding="utf-8")
    reader = HandoffReader()
    envelope = reader.read_path(baton)
    assert envelope.stage == "board-seed"
    assert envelope.outcome == "pass"


def test_read_path_plain_yaml_without_fence(tmp_path: Path) -> None:
    baton = tmp_path / "handoff.md"
    baton.write_text(_HANDOFF_BODY, encoding="utf-8")
    envelope = HandoffReader().read_path(str(baton))
    assert envelope.stage == "board-seed"


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
