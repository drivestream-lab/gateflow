"""Unit tests for pin checkpoint vocabulary (INIT-GATEFLOW-011 TASK-W0-02)."""

from src.business_services.workflow_engine import WorkflowEngine
from src.models.checkpoint_models import CheckpointEvidenceClassType


def test_get_github_checkpoint_vocab_resolves_six_ids() -> None:
    engine = WorkflowEngine()
    engine.load_pin()
    vocab = engine.get_github_checkpoint_vocab()
    assert set(vocab.by_checkpoint_id.keys()) == {
        "prd-impact-acceptance",
        "coding-readiness",
        "wave-acceptance",
        "wave-signoff",
        "initiative-closure-signoff-app",
        "initiative-closure-signoff-meta",
    }


def test_coding_readiness_vocab_from_pin_labels() -> None:
    engine = WorkflowEngine()
    engine.load_pin()
    entry = engine.get_github_checkpoint_vocab().by_checkpoint_id["coding-readiness"]
    assert entry.required_labels == ["spec-lgtm"]
    assert entry.blocking_labels == ["spec-blocked", "spec-revised", "spec-stale"]
    assert entry.review_role == "engineering-gate"
    assert entry.evidence_class == CheckpointEvidenceClassType.LABEL_AND_REVIEW


def test_wave_signoff_is_review_or_merge_class() -> None:
    engine = WorkflowEngine()
    engine.load_pin()
    entry = engine.get_github_checkpoint_vocab().by_checkpoint_id["wave-signoff"]
    assert entry.required_labels == []
    assert entry.blocking_labels == []
    assert entry.evidence_class == CheckpointEvidenceClassType.REVIEW_OR_MERGE
