"""Unit tests for HandoffReader and WorkflowEngine (TASK-W0-05)."""

from pathlib import Path

import pytest

from src.business_services.handoff_reader import HandoffReader
from src.business_services.workflow_engine import WorkflowEngine
from src.configs.programme_config_loader import load_programme_config
from src.models.handoff_models import HandoffEnvelope
from src.models.programme_config_models import ProgrammeConfig


@pytest.fixture(autouse=True)
def _programme_config(tmp_path: Path) -> ProgrammeConfig:
    ProgrammeConfig.reset_instance()
    return load_programme_config(Path("config/programme.yaml"))


def test_resolve_git_ref_prefers_pr_head() -> None:
    reader = HandoffReader()
    assert reader.resolve_git_ref(pr_head_sha="abc123", default_branch="develop") == "abc123"


def test_resolve_git_ref_falls_back_to_default_branch() -> None:
    reader = HandoffReader()
    assert reader.resolve_git_ref(pr_head_sha=None, default_branch="develop") == "develop"


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
    config = ProgrammeConfig.get_instance()
    # Override globs relative to tmp workspace
    config = config.model_copy(
        update={
            "handoff": config.handoff.model_copy(
                update={"artifact_globs": ["docs/specification/reports/**/*"]}
            )
        }
    )
    ProgrammeConfig.set_instance(config)
    reader = HandoffReader()
    envelope = reader.find_latest_handoff(tmp_path, programme_config=config)
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
    assert resolved.dispatch == "orchestrated"


def test_workflow_missing_pin_fails(tmp_path: Path) -> None:
    engine = WorkflowEngine()
    with pytest.raises(FileNotFoundError):
        engine.load_pin(workflow_path=tmp_path / "missing.yaml")
