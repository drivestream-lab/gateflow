"""Unit tests for RunOrchestrator branches (W1)."""

from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.business_services.policy_engine import PolicyEngine
from src.business_services.run_orchestrator import RunOrchestrator
from src.business_services.workflow_engine import WorkflowEngine
from src.models.control_plane_models import AgentRunResult
from src.models.policy_types import AgentRunOutcomeType
from src.models.run_store_models import JobModel, JobPayloadDocument, RunModel
from src.models.run_store_types import JobStatusType, RunStatusType


def _gate_stop_handoff(stage: str = "loop-spec") -> dict[str, object]:
    """Payload handoff that stops the walker after the executed stage."""
    return {
        "contract": "sdd-delivery/v2",
        "stage": stage,
        "outcome": "pass",
        "blockers": [],
        "human_checkpoint": True,
    }


def _dispatch_plan(
    *,
    start_node: str = "loop-spec",
    model_id: str = "cursor/fast",
) -> dict[str, object]:
    return {
        "start_node": start_node,
        "dispatch_plan": {
            "default": {"runner": "cursor", "model_id": model_id, "model_profile": "api"},
            "nodes": {},
        },
    }


def _job_payload(**extra: object) -> JobPayloadDocument:
    base: dict[str, object] = {
        "delivery_id": "d-run",
        "event_type": "pull_request",
        "repository": {
            "full_name": "acme/widget",
            "name": "widget",
            "owner": {"login": "acme"},
        },
        "pull_request": {"number": 7},
        "label": {"name": "gateflow:run-wave"},
        "workspace_path": str(Path.cwd()),
        "ticket_id": "55",
        "initiative_id": "INIT-GATEFLOW-005-BOUNDINPUT",
        **_dispatch_plan(),
        "handoff": _gate_stop_handoff(),
        **extra,
    }
    return JobPayloadDocument.model_validate(base)


def _build_orchestrator(**overrides: Any) -> RunOrchestrator:
    session = MagicMock()

    @asynccontextmanager
    async def txn():
        yield session

    postgres = MagicMock()
    postgres.transaction = txn

    run_id = uuid4()
    handoff_path = f"/tmp/gateflow-test-handoffs/{run_id}/handoff.md"
    run_repo = MagicMock()
    run_repo.create_run = AsyncMock(
        return_value=RunModel(
            id=run_id,
            org="acme",
            repo="widget",
            status_type=RunStatusType.ACTIVE,
            pr_number=7,
            handoff_path=handoff_path,
            retry_counter=0,
            notify_pending=False,
            created_at=datetime.now(UTC),
        )
    )
    run_repo.update_run = AsyncMock(
        side_effect=lambda _s, _id, update: RunModel(
            id=run_id,
            org="acme",
            repo="widget",
            status_type=update.status_type or RunStatusType.ACTIVE,
            outcome_type=update.outcome_type,
            workflow_node=update.workflow_node,
            pr_number=update.pr_number if update.pr_number is not None else 7,
            wave_duration_ms=update.wave_duration_ms,
            handoff_path=(update.handoff_path if update.handoff_path is not None else handoff_path),
            retry_counter=0,
            notify_pending=(update.notify_pending if update.notify_pending is not None else False),
            created_at=datetime.now(UTC),
        )
    )

    trigger_router = MagicMock()
    handoff_reader = MagicMock()
    notifier = MagicMock()
    notifier.notify_precondition_failure = AsyncMock(return_value=False)
    notifier.post_run_event_comment = AsyncMock(return_value=False)
    metrics_emitter = MagicMock()
    metrics_emitter.record_stage_duration = AsyncMock()
    launchpad_client = MagicMock()
    launchpad_client.sync_harness = AsyncMock()
    cursor_agent_runner = MagicMock()
    run_event_repo = MagicMock()
    run_event_repo.append_event = AsyncMock()
    stage_repo = MagicMock()
    stage_repo.create_stage = AsyncMock()
    forge_client = MagicMock()
    forge_client.ensure_branch_from_base = AsyncMock(return_value=True)
    forge_client.create_or_update_pull_request = AsyncMock(return_value=42)
    workflow_engine = WorkflowEngine()
    workflow_engine.load_pin()
    policy_engine = PolicyEngine(workflow_engine=workflow_engine)
    from src.business_services.prompt_resolver import PromptResolver

    prompt_resolver = PromptResolver()

    defaults = {
        "postgres_service": postgres,
        "trigger_router": trigger_router,
        "policy_engine": policy_engine,
        "workflow_engine": workflow_engine,
        "handoff_reader": handoff_reader,
        "notifier": notifier,
        "metrics_emitter": metrics_emitter,
        "launchpad_client": launchpad_client,
        "cursor_agent_runner": cursor_agent_runner,
        "forge_client": forge_client,
        "run_repository": run_repo,
        "run_event_repository": run_event_repo,
        "stage_repository": stage_repo,
        "prompt_resolver": prompt_resolver,
    }
    defaults.update(overrides)
    return RunOrchestrator(**defaults)


@pytest.mark.asyncio
async def test_concurrent_reject_path_not_dispatched() -> None:
    from src.models.control_plane_models import (
        PreconditionFailure,
        TriggerAuthorizationResult,
        TriggerContext,
    )
    from src.models.policy_types import WavePreconditionIdType

    trigger_router = MagicMock()
    trigger_router.authorize_and_check = AsyncMock(
        return_value=TriggerAuthorizationResult(
            authorized=False,
            context=TriggerContext(
                org="acme",
                repo="widget",
                event_type="pull_request",
                delivery_id="d-run",
                trigger_label="gateflow:run-wave",
                pr_number=7,
            ),
            failures=[
                PreconditionFailure(
                    precondition_id=WavePreconditionIdType.NO_CONCURRENT_RUN,
                    reason="Active run exists",
                )
            ],
        )
    )
    orchestrator = _build_orchestrator(trigger_router=trigger_router)
    summary = await orchestrator.process_job(
        JobModel(
            id=uuid4(),
            status_type=JobStatusType.CLAIMED,
            payload=_job_payload(),
            delivery_id="d-run",
        )
    )
    assert summary.dispatched is False
    assert summary.run_id is None
    assert summary.terminal_status == "not_dispatched"


@pytest.mark.asyncio
async def test_enter_at_missing_start_node_fails() -> None:
    from src.models.control_plane_models import (
        TriggerAuthorizationResult,
        TriggerContext,
    )

    trigger_router = MagicMock()
    trigger_router.authorize_and_check = AsyncMock(
        return_value=TriggerAuthorizationResult(
            authorized=True,
            context=TriggerContext(
                org="acme",
                repo="widget",
                event_type="api_trigger",
                delivery_id="d-run",
                trigger_label="gateflow:run-wave",
                pr_number=7,
            ),
            failures=[],
        )
    )
    orchestrator = _build_orchestrator(trigger_router=trigger_router)
    payload = _job_payload()
    raw = payload.model_dump()
    raw.pop("start_node", None)
    raw.pop("dispatch_plan", None)
    job = JobModel(
        id=uuid4(),
        status_type=JobStatusType.CLAIMED,
        payload=JobPayloadDocument.model_validate(raw),
        delivery_id="d-run",
    )
    summary = await orchestrator.process_job(job)
    assert summary.dispatched is False
    assert summary.run_id is not None
    assert summary.terminal_status == RunStatusType.FAILED.value


@pytest.mark.asyncio
async def test_agent_failure_marks_run_failed() -> None:
    from src.models.control_plane_models import (
        TriggerAuthorizationResult,
        TriggerContext,
    )

    trigger_router = MagicMock()
    trigger_router.authorize_and_check = AsyncMock(
        return_value=TriggerAuthorizationResult(
            authorized=True,
            context=TriggerContext(
                org="acme",
                repo="widget",
                event_type="pull_request",
                delivery_id="d-run",
                trigger_label="gateflow:run-wave",
                pr_number=7,
                workspace_path=str(Path.cwd()),
            ),
            failures=[],
        )
    )
    cursor_agent_runner = MagicMock()
    cursor_agent_runner.run_skill = AsyncMock(
        return_value=AgentRunResult(
            runner="cursor",
            outcome=AgentRunOutcomeType.FAILED,
            error_message="forced",
        )
    )
    metrics_emitter = MagicMock()
    metrics_emitter.record_stage_duration = AsyncMock()
    stage_repo = MagicMock()
    stage_repo.create_stage = AsyncMock()
    run_repo = MagicMock()
    run_id = uuid4()
    run_repo.create_run = AsyncMock(
        return_value=RunModel(
            id=run_id,
            org="acme",
            repo="widget",
            status_type=RunStatusType.ACTIVE,
            pr_number=7,
            handoff_path=f"/tmp/gateflow-test-handoffs/{run_id}/handoff.md",
            retry_counter=0,
            notify_pending=False,
            created_at=datetime.now(UTC),
        )
    )
    run_repo.update_run = AsyncMock(
        side_effect=lambda _s, _id, update: RunModel(
            id=run_id,
            org="acme",
            repo="widget",
            status_type=update.status_type or RunStatusType.ACTIVE,
            outcome_type=update.outcome_type,
            workflow_node=update.workflow_node,
            pr_number=update.pr_number if update.pr_number is not None else 7,
            wave_duration_ms=update.wave_duration_ms,
            handoff_path=update.handoff_path or f"/tmp/gateflow-test-handoffs/{run_id}/handoff.md",
            retry_counter=0,
            notify_pending=(update.notify_pending if update.notify_pending is not None else False),
            created_at=datetime.now(UTC),
        )
    )
    orchestrator = _build_orchestrator(
        trigger_router=trigger_router,
        cursor_agent_runner=cursor_agent_runner,
        metrics_emitter=metrics_emitter,
        stage_repository=stage_repo,
        run_repository=run_repo,
    )
    summary = await orchestrator.process_job(
        JobModel(
            id=uuid4(),
            status_type=JobStatusType.CLAIMED,
            payload=_job_payload(event_type="api_trigger"),
            delivery_id="d-run",
        )
    )
    assert summary.dispatched is True
    assert summary.terminal_status == RunStatusType.FAILED.value
    assert summary.stop_reason == "forced"
    metrics_emitter.record_stage_duration.assert_awaited()
    assert metrics_emitter.record_stage_duration.await_args.kwargs["outcome"] == "failed"
    stage_repo.create_stage.assert_awaited()
    stage_create = stage_repo.create_stage.await_args.args[1]
    from src.models.run_store_types import RunOutcomeType

    assert stage_create.outcome_type == RunOutcomeType.FAILED
    assert stage_create.runner == "cursor"
    assert stage_create.workflow_node == "loop-spec"
    update = run_repo.update_run.await_args.args[2]
    assert isinstance(update.wave_duration_ms, int)
    assert update.wave_duration_ms >= 0


@pytest.mark.asyncio
async def test_dispatch_persists_resolved_runner_and_model_fields() -> None:
    from src.models.control_plane_models import (
        TriggerAuthorizationResult,
        TriggerContext,
    )

    trigger_router = MagicMock()
    trigger_router.authorize_and_check = AsyncMock(
        return_value=TriggerAuthorizationResult(
            authorized=True,
            context=TriggerContext(
                org="acme",
                repo="widget",
                event_type="api_trigger",
                delivery_id="d-run",
                trigger_label="gateflow:run-wave",
                pr_number=7,
                workspace_path=str(Path.cwd()),
            ),
            failures=[],
        )
    )
    cursor_agent_runner = MagicMock()
    cursor_agent_runner.run_skill = AsyncMock(
        return_value=AgentRunResult(
            runner="cursor",
            outcome=AgentRunOutcomeType.SUCCESS,
            model_profile="api",
            model_id="cursor/fast",
            model_provider="cursor",
        )
    )
    stage_repo = MagicMock()
    stage_repo.create_stage = AsyncMock()
    forge_client = MagicMock()
    forge_client.ensure_branch_from_base = AsyncMock(return_value=True)
    forge_client.create_or_update_pull_request = AsyncMock(return_value=99)

    orchestrator = _build_orchestrator(
        trigger_router=trigger_router,
        cursor_agent_runner=cursor_agent_runner,
        stage_repository=stage_repo,
        forge_client=forge_client,
    )
    summary = await orchestrator.process_job(
        JobModel(
            id=uuid4(),
            status_type=JobStatusType.CLAIMED,
            payload=_job_payload(event_type="api_trigger"),
            delivery_id="d-run",
        )
    )
    assert summary.dispatched is True
    assert summary.terminal_status == RunStatusType.STOPPED.value
    stage_repo.create_stage.assert_awaited()
    stage_create = stage_repo.create_stage.await_args.args[1]
    assert stage_create.runner == "cursor"
    assert stage_create.model_profile == "api"
    assert stage_create.model_id == "cursor/fast"
    assert stage_create.model_provider == "cursor"
    cursor_agent_runner.run_skill.assert_awaited()
    call_kwargs = cursor_agent_runner.run_skill.await_args.kwargs
    assert call_kwargs["model_profile"] == "api"
    assert call_kwargs["model_id"] == "cursor/fast"
    assert call_kwargs.get("message")
    assert stage_create.prompt_id == "loop-spec"
    assert stage_create.prompt_revision


@pytest.mark.asyncio
async def test_pr_opened_before_stage_when_run_has_no_pr() -> None:
    from src.models.control_plane_models import (
        TriggerAuthorizationResult,
        TriggerContext,
    )

    run_id = uuid4()
    run_repo = MagicMock()
    run_repo.create_run = AsyncMock(
        return_value=RunModel(
            id=run_id,
            org="acme",
            repo="widget",
            status_type=RunStatusType.ACTIVE,
            pr_number=None,
            initiative_id="INIT-ACME-001",
            wave_id="W1",
            retry_counter=0,
            notify_pending=False,
        )
    )
    run_repo.update_run = AsyncMock(
        side_effect=lambda _s, _id, update: RunModel(
            id=run_id,
            org="acme",
            repo="widget",
            status_type=update.status_type or RunStatusType.ACTIVE,
            outcome_type=update.outcome_type,
            workflow_node=update.workflow_node,
            pr_number=update.pr_number if update.pr_number is not None else 55,
            initiative_id="INIT-ACME-001",
            wave_id="W1",
            retry_counter=0,
            notify_pending=update.notify_pending or False,
        )
    )
    trigger_router = MagicMock()
    trigger_router.authorize_and_check = AsyncMock(
        return_value=TriggerAuthorizationResult(
            authorized=True,
            context=TriggerContext(
                org="acme",
                repo="widget",
                event_type="api_trigger",
                delivery_id="d-run",
                trigger_label="gateflow:run-wave",
                workspace_path=str(Path.cwd()),
                initiative_id="INIT-ACME-001",
            ),
            failures=[],
        )
    )
    cursor_agent_runner = MagicMock()
    cursor_agent_runner.run_skill = AsyncMock(
        return_value=AgentRunResult(
            runner="cursor",
            outcome=AgentRunOutcomeType.SUCCESS,
            model_profile="api",
            model_id="cursor/auto",
            model_provider="cursor",
        )
    )
    forge_client = MagicMock()
    forge_client.ensure_branch_from_base = AsyncMock(return_value=True)
    forge_client.create_or_update_pull_request = AsyncMock(return_value=55)
    stage_repo = MagicMock()
    stage_repo.create_stage = AsyncMock()

    call_order: list[str] = []

    async def _pr(*_a: object, **_k: object) -> int:
        call_order.append("pr")
        return 55

    async def _stage(*_a: object, **_k: object) -> None:
        call_order.append("stage")

    forge_client.create_or_update_pull_request = AsyncMock(side_effect=_pr)
    stage_repo.create_stage = AsyncMock(side_effect=_stage)

    orchestrator = _build_orchestrator(
        trigger_router=trigger_router,
        cursor_agent_runner=cursor_agent_runner,
        forge_client=forge_client,
        run_repository=run_repo,
        stage_repository=stage_repo,
    )
    summary = await orchestrator.process_job(
        JobModel(
            id=uuid4(),
            status_type=JobStatusType.CLAIMED,
            payload=_job_payload(
                event_type="api_trigger",
                pr_number=None,
                initiative_id="INIT-ACME-001",
                wave_id="W1",
                branch_slug="pr-order",
                base_branch="develop",
                **_dispatch_plan(start_node="ground-spec", model_id="cursor/auto"),
                handoff=_gate_stop_handoff("ground-spec"),
            ),
            delivery_id="d-run",
        )
    )
    assert summary.dispatched is True
    assert call_order == ["pr", "stage"]
    forge_client.ensure_branch_from_base.assert_awaited()
    forge_client.create_or_update_pull_request.assert_awaited()
    pr_kwargs = forge_client.create_or_update_pull_request.await_args.kwargs
    assert pr_kwargs["head"] == "feature/INIT-ACME-001-w1-pr-order"
    assert pr_kwargs["base"] == "develop"


@pytest.mark.asyncio
async def test_process_job_never_calls_board_forge_mutations() -> None:
    """FR-24 worker isolation — completing a wave job must not mutate board tickets."""
    from src.models.control_plane_models import (
        TriggerAuthorizationResult,
        TriggerContext,
    )

    trigger_router = MagicMock()
    trigger_router.authorize_and_check = AsyncMock(
        return_value=TriggerAuthorizationResult(
            authorized=True,
            context=TriggerContext(
                org="acme",
                repo="widget",
                event_type="api_trigger",
                delivery_id="d-run",
                trigger_label="gateflow:run-wave",
                pr_number=7,
                workspace_path=str(Path.cwd()),
            ),
            failures=[],
        )
    )
    cursor_agent_runner = MagicMock()
    cursor_agent_runner.run_skill = AsyncMock(
        return_value=AgentRunResult(
            runner="cursor",
            outcome=AgentRunOutcomeType.SUCCESS,
            model_profile="api",
            model_id="cursor/fast",
            model_provider="cursor",
        )
    )
    forge_client = MagicMock()
    forge_client.ensure_branch_from_base = AsyncMock(return_value=True)
    forge_client.create_or_update_pull_request = AsyncMock(return_value=42)
    forge_client.update_issue_status = AsyncMock()
    forge_client.link_pull_request = AsyncMock()
    forge_client.create_issue = AsyncMock()
    forge_client.apply_issue_labels = AsyncMock()
    forge_client.find_issues_by_labels = AsyncMock()

    orchestrator = _build_orchestrator(
        trigger_router=trigger_router,
        cursor_agent_runner=cursor_agent_runner,
        forge_client=forge_client,
    )
    summary = await orchestrator.process_job(
        JobModel(
            id=uuid4(),
            status_type=JobStatusType.CLAIMED,
            payload=_job_payload(event_type="api_trigger"),
            delivery_id="d-run",
        )
    )
    assert summary.dispatched is True
    forge_client.update_issue_status.assert_not_called()
    forge_client.link_pull_request.assert_not_called()
    forge_client.create_issue.assert_not_called()
    forge_client.apply_issue_labels.assert_not_called()
    forge_client.find_issues_by_labels.assert_not_called()


def _authorized_api_trigger() -> MagicMock:
    from src.models.control_plane_models import (
        TriggerAuthorizationResult,
        TriggerContext,
    )

    trigger_router = MagicMock()
    trigger_router.authorize_and_check = AsyncMock(
        return_value=TriggerAuthorizationResult(
            authorized=True,
            context=TriggerContext(
                org="acme",
                repo="widget",
                event_type="api_trigger",
                delivery_id="d-run",
                trigger_label="gateflow:run-wave",
                pr_number=7,
                workspace_path=str(Path.cwd()),
            ),
            failures=[],
        )
    )
    return trigger_router


@pytest.mark.asyncio
async def test_walker_continues_then_stops_at_gate() -> None:
    from src.models.handoff_models import HandoffEnvelope

    cursor_agent_runner = MagicMock()
    cursor_agent_runner.run_skill = AsyncMock(
        return_value=AgentRunResult(
            runner="cursor",
            outcome=AgentRunOutcomeType.SUCCESS,
            model_profile="api",
            model_id="cursor/fast",
            model_provider="cursor",
        )
    )
    handoff_reader = MagicMock()
    handoff_reader.find_latest_handoff = MagicMock(
        side_effect=[
            HandoffEnvelope(
                contract="sdd-delivery/v2",
                stage="loop-spec",
                outcome="pass",
                blockers=[],
                human_checkpoint=False,
            ),
            HandoffEnvelope(
                contract="sdd-delivery/v2",
                stage="verify",
                outcome="pass",
                blockers=[],
                human_checkpoint=True,
            ),
        ]
    )
    stage_repo = MagicMock()
    stage_repo.create_stage = AsyncMock()
    raw = _job_payload(event_type="api_trigger").model_dump()
    raw.pop("handoff", None)
    orchestrator = _build_orchestrator(
        trigger_router=_authorized_api_trigger(),
        cursor_agent_runner=cursor_agent_runner,
        handoff_reader=handoff_reader,
        stage_repository=stage_repo,
    )
    summary = await orchestrator.process_job(
        JobModel(
            id=uuid4(),
            status_type=JobStatusType.CLAIMED,
            payload=JobPayloadDocument.model_validate(raw),
            delivery_id="d-run",
        )
    )
    assert summary.dispatched is True
    assert summary.terminal_status == RunStatusType.STOPPED.value
    assert stage_repo.create_stage.await_count == 2
    assert cursor_agent_runner.run_skill.await_count == 2


@pytest.mark.asyncio
async def test_walker_hop_cap_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    from src.configs.orchestration_settings import OrchestrationSettings
    from src.models.handoff_models import HandoffEnvelope

    monkeypatch.setenv("GATEFLOW_MAX_ORCHESTRATED_HOPS", "1")
    OrchestrationSettings._instances.pop("OrchestrationSettings", None)

    cursor_agent_runner = MagicMock()
    cursor_agent_runner.run_skill = AsyncMock(
        return_value=AgentRunResult(
            runner="cursor",
            outcome=AgentRunOutcomeType.SUCCESS,
            model_profile="api",
            model_id="cursor/fast",
            model_provider="cursor",
        )
    )
    handoff_reader = MagicMock()
    handoff_reader.find_latest_handoff = MagicMock(
        return_value=HandoffEnvelope(
            contract="sdd-delivery/v2",
            stage="loop-spec",
            outcome="pass",
            blockers=[],
            human_checkpoint=False,
        )
    )
    raw = _job_payload(event_type="api_trigger").model_dump()
    raw.pop("handoff", None)
    orchestrator = _build_orchestrator(
        trigger_router=_authorized_api_trigger(),
        cursor_agent_runner=cursor_agent_runner,
        handoff_reader=handoff_reader,
    )
    summary = await orchestrator.process_job(
        JobModel(
            id=uuid4(),
            status_type=JobStatusType.CLAIMED,
            payload=JobPayloadDocument.model_validate(raw),
            delivery_id="d-run",
        )
    )
    assert summary.dispatched is True
    assert summary.terminal_status == RunStatusType.FAILED.value
    assert summary.stop_reason is not None
    assert "Max orchestrated hops" in summary.stop_reason
    assert cursor_agent_runner.run_skill.await_count == 1
    OrchestrationSettings._instances.pop("OrchestrationSettings", None)
