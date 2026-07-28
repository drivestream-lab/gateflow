"""Unit tests for TriggerRouter and PolicyEngine (W1 control plane)."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.business_services.policy_engine import PolicyEngine
from src.business_services.trigger_router import TriggerRouter
from src.models.handoff_models import HandoffEnvelope
from src.models.policy_types import PolicyDecisionType, WavePreconditionIdType
from src.models.run_store_models import RunModel
from src.models.run_store_types import RunStatusType


def _labeled_payload(label: str = "gateflow:run-wave") -> dict[str, object]:
    return {
        "repository": {"full_name": "acme/widget", "name": "widget", "owner": {"login": "acme"}},
        "pull_request": {"number": 42},
        "label": {"name": label},
    }


@pytest.mark.asyncio
async def test_label_wave_start_disabled() -> None:
    run_repo = MagicMock()
    run_repo.find_active_run = AsyncMock(return_value=None)
    router = TriggerRouter(run_repository=run_repo)
    session = MagicMock()
    result = await router.authorize_and_check(
        session,
        event_type="pull_request",
        delivery_id="d1",
        payload=_labeled_payload("gateflow:run-wave"),
    )
    assert result.authorized is False
    assert any(f.precondition_id == WavePreconditionIdType.TRIGGER_LABEL for f in result.failures)
    assert any("disabled" in f.reason for f in result.failures)


@pytest.mark.asyncio
async def test_api_trigger_concurrent_active_run_rejected() -> None:
    active = RunModel(
        id=uuid4(),
        org="acme",
        repo="widget",
        status_type=RunStatusType.ACTIVE,
        initiative_id="INIT-X",
        wave_id="W0",
        retry_counter=0,
        notify_pending=False,
    )
    run_repo = MagicMock()
    run_repo.find_active_run = AsyncMock(return_value=active)
    router = TriggerRouter(run_repository=run_repo)
    result = await router.authorize_and_check(
        MagicMock(),
        event_type="api_trigger",
        delivery_id="d2",
        payload={
            "org": "acme",
            "repo": "widget",
            "initiative_id": "INIT-X",
            "wave_id": "W0",
            "trigger_source": "api",
        },
    )
    assert result.authorized is False
    assert any(
        f.precondition_id == WavePreconditionIdType.NO_CONCURRENT_RUN for f in result.failures
    )


@pytest.mark.asyncio
async def test_api_trigger_authorized() -> None:
    run_repo = MagicMock()
    run_repo.find_active_run = AsyncMock(return_value=None)
    router = TriggerRouter(run_repository=run_repo)
    result = await router.authorize_and_check(
        MagicMock(),
        event_type="api_trigger",
        delivery_id="d3",
        payload={
            "org": "acme",
            "repo": "widget",
            "initiative_id": "INIT-X",
            "wave_id": "W0",
            "trigger_source": "api",
        },
    )
    assert result.authorized is True
    assert result.context is not None
    assert result.context.org == "acme"


def test_policy_dispatch_only_skill_orchestrated() -> None:
    engine = MagicMock()
    from src.models.handoff_models import ResolvedWorkflowNode

    engine.resolve_next.return_value = ResolvedWorkflowNode(
        node_id="pre-implement",
        node_type="skill",
        dispatch="orchestrated",
    )
    policy = PolicyEngine(workflow_engine=engine)
    handoff = HandoffEnvelope(
        contract="sdd-delivery/v2",
        stage="board-seed",
        outcome="pass",
    )
    trigger = MagicMock()
    decision = policy.evaluate_dispatch(handoff, trigger)
    assert decision.decision == PolicyDecisionType.DISPATCH
    assert decision.next_node is not None
    assert decision.next_node.node_id == "pre-implement"


def test_policy_human_checkpoint_true_does_not_veto_orchestrated_skill() -> None:
    """workflow.yaml is dispatch SSOT; envelope human_checkpoint only WARNs on mismatch."""
    from src.models.handoff_models import ResolvedWorkflowNode

    engine = MagicMock()
    engine.resolve_next.return_value = ResolvedWorkflowNode(
        node_id="loop-spec",
        node_type="skill",
        dispatch="orchestrated",
    )
    policy = PolicyEngine(workflow_engine=engine)
    policy.logger = MagicMock()
    handoff = HandoffEnvelope(
        contract="sdd-delivery/v2",
        stage="pre-implement",
        outcome="pass",
        human_checkpoint=True,
    )
    decision = policy.evaluate_dispatch(handoff, MagicMock())
    assert decision.decision == PolicyDecisionType.DISPATCH
    assert decision.next_node is not None
    assert decision.next_node.node_id == "loop-spec"
    policy.logger.warning.assert_called_once()
    warn_msg = policy.logger.warning.call_args.args[0]
    assert "human_checkpoint disagrees" in warn_msg


def test_policy_stop_on_pin_human_checkpoint_node() -> None:
    from src.models.handoff_models import ResolvedWorkflowNode

    engine = MagicMock()
    engine.resolve_next.return_value = ResolvedWorkflowNode(
        node_id="wave-human-decision",
        node_type="human-checkpoint",
        dispatch=None,
    )
    policy = PolicyEngine(workflow_engine=engine)
    handoff = HandoffEnvelope(
        contract="sdd-delivery/v2",
        stage="ground-spec",
        outcome="pass",
        human_checkpoint=True,
    )
    decision = policy.evaluate_dispatch(handoff, MagicMock())
    assert decision.decision == PolicyDecisionType.STOP
    assert decision.next_node is not None
    assert decision.next_node.node_id == "wave-human-decision"
    assert "human-checkpoint" in (decision.block_reason or "")


def test_policy_block_on_contract_mismatch() -> None:
    engine = MagicMock()
    engine.resolve_next.side_effect = ValueError(
        "Handoff contract 'other/v1' does not match installed 'sdd-delivery/v2'"
    )
    policy = PolicyEngine(workflow_engine=engine)
    handoff = HandoffEnvelope(
        contract="other/v1",
        stage="board-seed",
        outcome="pass",
    )
    decision = policy.evaluate_dispatch(handoff, MagicMock())
    assert decision.decision == PolicyDecisionType.BLOCK


def test_policy_findings_budget_stop(monkeypatch: pytest.MonkeyPatch) -> None:
    from src.configs.orchestration_settings import OrchestrationSettings

    monkeypatch.setenv("GATEFLOW_FINDINGS_BUDGET", "2")
    OrchestrationSettings._instances.pop("OrchestrationSettings", None)
    policy = PolicyEngine(workflow_engine=MagicMock())
    handoff = HandoffEnvelope(
        contract="sdd-delivery/v2",
        stage="loop-spec",
        outcome="findings",
    )
    decision = policy.evaluate_dispatch(handoff, MagicMock(), retry_counter=2)
    assert decision.decision == PolicyDecisionType.STOP
    assert "Retry budget exhausted" in (decision.block_reason or "")
    OrchestrationSettings._instances.pop("OrchestrationSettings", None)
