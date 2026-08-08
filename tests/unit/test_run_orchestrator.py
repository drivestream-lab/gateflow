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
    """Handoff that stops the walker via pin (blockers → STOP), not flag alone.

    Envelope ``human_checkpoint`` is no longer a PolicyEngine veto; use unresolved
    blockers (or an outcome that resolves to ``human-checkpoint``) to halt tests.
    """
    return {
        "contract": "sdd-delivery/v2",
        "stage": stage,
        "outcome": "blocked",
        "blockers": ["TEST-WALKER-STOP"],
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
        "initiative_id": "INIT-GATEFLOW-008",
        "wave_id": "w1",
        "branch_slug": "implement-lane",
        "base_branch": "develop",
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
    from src.models.handoff_models import HandoffEnvelope

    handoff_reader = MagicMock()
    handoff_reader.read_path = MagicMock(
        return_value=HandoffEnvelope(
            contract="sdd-delivery/v2",
            stage="loop-spec",
            outcome="blocked",
            blockers=["TEST-WALKER-STOP"],
            human_checkpoint=True,
        )
    )
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
    # Default: remote head missing → new-wave path calls ensure_branch_from_base.
    forge_client.get_branch_tip_sha = AsyncMock(side_effect=ValueError("branch missing"))
    forge_client.create_or_update_pull_request = AsyncMock(return_value=42)
    forge_client.open_draft_pr = AsyncMock(return_value=42)
    forge_client.commit_paths_to_branch = AsyncMock(
        return_value=MagicMock(
            commit_sha="abc123",
            branch="gateflow/x",
            path_count=0,
            paths=[],
        )
    )
    forge_action_service = MagicMock()
    forge_action_service.apply_external_action = AsyncMock(
        return_value=MagicMock(pr_number=99, action=MagicMock(value="open_draft_pr"))
    )
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
        "forge_action_service": forge_action_service,
        "run_repository": run_repo,
        "run_event_repository": run_event_repo,
        "stage_repository": stage_repo,
        "prompt_resolver": prompt_resolver,
        "learning_ingest_service": MagicMock(
            ingest_after_learning_extract=AsyncMock(return_value=None)
        ),
        "tenant_service": MagicMock(get_workspace_credential_for_repo=AsyncMock(return_value=None)),
        "tenant_git_workspace_client": MagicMock(
            resolve_workspace=AsyncMock(),
            checkout_branch=AsyncMock(),
        ),
    }
    defaults.update(overrides)
    orch = RunOrchestrator(**defaults)
    # Walker unit tests use Path.cwd(); stub publish so dirty trees do not force forge.
    # Dedicated forge-publish tests replace this method or call it directly.
    orch._publish_stage_workspace_if_needed = AsyncMock(return_value=None)  # type: ignore[method-assign]
    return orch


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
async def test_ensure_branch_before_stage_when_run_has_no_pr() -> None:
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
            pr_number=update.pr_number,
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
    forge_client.get_branch_tip_sha = AsyncMock(side_effect=ValueError("branch missing"))
    forge_client.create_or_update_pull_request = AsyncMock(return_value=55)
    stage_repo = MagicMock()
    stage_repo.create_stage = AsyncMock()

    call_order: list[str] = []

    async def _branch(*_a: object, **_k: object) -> bool:
        call_order.append("ensure_branch")
        return True

    async def _stage(*_a: object, **_k: object) -> None:
        call_order.append("stage")

    forge_client.ensure_branch_from_base = AsyncMock(side_effect=_branch)
    stage_repo.create_stage = AsyncMock(side_effect=_stage)

    from src.models.handoff_models import HandoffEnvelope

    handoff_reader = MagicMock()
    handoff_reader.read_path = MagicMock(
        return_value=HandoffEnvelope(
            contract="sdd-delivery/v2",
            stage="ground-spec",
            outcome="pass",
            blockers=[],
            human_checkpoint=True,
        )
    )

    orchestrator = _build_orchestrator(
        trigger_router=trigger_router,
        cursor_agent_runner=cursor_agent_runner,
        forge_client=forge_client,
        run_repository=run_repo,
        stage_repository=stage_repo,
        handoff_reader=handoff_reader,
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
            ),
            delivery_id="d-run",
        )
    )
    assert summary.dispatched is True
    assert call_order == ["ensure_branch", "stage"]
    forge_client.ensure_branch_from_base.assert_awaited()
    forge_client.create_or_update_pull_request.assert_not_awaited()
    branch_kwargs = forge_client.ensure_branch_from_base.await_args.kwargs
    assert branch_kwargs["branch"] == "feature/INIT-ACME-001-w1-pr-order"
    assert branch_kwargs["base"] == "develop"


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
    forge_client.commit_paths_to_branch = AsyncMock(
        return_value=MagicMock(
            commit_sha="abc123",
            branch="gateflow/x",
            path_count=0,
            paths=[],
        )
    )
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
    from src.models.forge_models import HandoffForgeDocument
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
    # Pass-1: pre-implement → loop-spec → automated wave-pr apply → wave-acceptance STOP.
    handoff_reader.read_path = MagicMock(
        side_effect=[
            HandoffEnvelope(
                contract="sdd-delivery/v2",
                stage="pre-implement",
                outcome="pass",
                blockers=[],
                human_checkpoint=False,
            ),
            HandoffEnvelope(
                contract="sdd-delivery/v2",
                stage="loop-spec",
                outcome="pass",
                blockers=[],
                human_checkpoint=False,
                forge=HandoffForgeDocument(
                    title="W1 draft",
                    body_path="docs/body.md",
                ),
            ),
        ]
    )
    stage_repo = MagicMock()
    stage_repo.create_stage = AsyncMock()
    run_event_repo = MagicMock()
    run_event_repo.append_event = AsyncMock()
    forge_action = MagicMock()
    forge_action.apply_external_action = AsyncMock(
        return_value=MagicMock(pr_number=88, action=MagicMock(value="open_draft_pr"))
    )
    raw = _job_payload(event_type="api_trigger").model_dump()
    raw.pop("handoff", None)
    raw.update(_dispatch_plan(start_node="pre-implement"))
    orchestrator = _build_orchestrator(
        trigger_router=_authorized_api_trigger(),
        cursor_agent_runner=cursor_agent_runner,
        handoff_reader=handoff_reader,
        stage_repository=stage_repo,
        run_event_repository=run_event_repo,
        forge_action_service=forge_action,
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
    assert summary.stop_reason is not None
    assert "wave-acceptance" in summary.stop_reason
    assert stage_repo.create_stage.await_count == 2
    assert cursor_agent_runner.run_skill.await_count == 2
    assert handoff_reader.read_path.call_count == 2
    forge_action.apply_external_action.assert_awaited_once()
    stopped_events = [
        call.args[1]
        for call in run_event_repo.append_event.await_args_list
        if call.args[1].event_type == "run_stopped"
    ]
    assert len(stopped_events) == 1
    assert stopped_events[0].payload.get("purpose") == "wave-acceptance"
    assert "owner" not in stopped_events[0].payload


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
    # Need two orchestrated hops in a row: pre-implement → loop-spec (before wave-acceptance).
    handoff_reader.read_path = MagicMock(
        return_value=HandoffEnvelope(
            contract="sdd-delivery/v2",
            stage="pre-implement",
            outcome="pass",
            blockers=[],
            human_checkpoint=False,
        )
    )
    raw = _job_payload(event_type="api_trigger").model_dump()
    raw.pop("handoff", None)
    raw.update(_dispatch_plan(start_node="pre-implement"))
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


@pytest.mark.asyncio
async def test_packaged_ingest_uses_read_path_not_ambient() -> None:
    """REQ-8b: success ingest calls read_path(stored) only."""
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
    handoff_reader.read_path = MagicMock(
        return_value=HandoffEnvelope(
            contract="sdd-delivery/v2",
            stage="loop-spec",
            outcome="blocked",
            blockers=["TEST-WALKER-STOP"],
            human_checkpoint=True,
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
            delivery_id="d-ingest",
        )
    )
    assert summary.dispatched is True
    assert summary.terminal_status == RunStatusType.STOPPED.value
    handoff_reader.read_path.assert_called()
    stored = handoff_reader.read_path.call_args.args[0]
    assert isinstance(stored, str)
    assert stored.endswith("/handoff.md")


@pytest.mark.asyncio
async def test_packaged_ingest_missing_path_fails_closed() -> None:
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
    handoff_reader.read_path = MagicMock(
        side_effect=ValueError("Handoff path missing or not a file: /missing/handoff.md")
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
            delivery_id="d-ingest-fail",
        )
    )
    assert summary.dispatched is True
    assert summary.terminal_status == RunStatusType.FAILED.value
    assert summary.stop_reason is not None
    assert "missing" in summary.stop_reason.lower() or "Handoff path" in summary.stop_reason


@pytest.mark.asyncio
async def test_publish_stage_workspace_required_empty_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:

    orch = _build_orchestrator()
    # Restore real publisher (helper stubs it).
    from src.business_services.run_orchestrator import RunOrchestrator as RO

    orch._publish_stage_workspace_if_needed = RO._publish_stage_workspace_if_needed.__get__(
        orch, RO
    )

    forge = MagicMock()
    forge.get_branch_tip_sha = AsyncMock(return_value="abc123def456")
    orch._forge_client = forge
    monkeypatch.setattr(
        "src.business_services.run_orchestrator.collect_commit_paths",
        lambda *_a, **_k: [],
    )
    run = RunModel(
        id=uuid4(),
        org="acme",
        repo="widget",
        status_type=RunStatusType.ACTIVE,
        initiative_id="INIT-GATEFLOW-006",
        wave_id="w1",
        created_at=datetime.now(UTC),
    )
    with pytest.raises(ValueError, match="required"):
        await orch._publish_stage_workspace_if_needed(
            MagicMock(),
            run=run,
            workspace_path=str(tmp_path),
            node_id="loop-spec",
            payload={
                "initiative_id": "INIT-GATEFLOW-006",
                "wave_id": "w1",
                "branch_slug": "forge-commit",
            },
        )
    forge.get_branch_tip_sha.assert_awaited()


@pytest.mark.asyncio
async def test_publish_stage_workspace_optional_commits(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from src.models.forge_models import CommitPathsResult

    orch = _build_orchestrator()
    from src.business_services.run_orchestrator import RunOrchestrator as RO

    orch._publish_stage_workspace_if_needed = RO._publish_stage_workspace_if_needed.__get__(
        orch, RO
    )
    forge = MagicMock()
    forge.get_branch_tip_sha = AsyncMock(return_value="abc123def456")
    forge.commit_paths_to_branch = AsyncMock(
        return_value=CommitPathsResult(
            commit_sha="deadbeef",
            branch="feature/INIT-GATEFLOW-006-w1-forge-commit",
            path_count=1,
            paths=["docs/a.md"],
        )
    )
    orch._forge_client = forge
    events = MagicMock()
    events.append_event = AsyncMock()
    orch._run_event_repository = events

    def _collect(_ws: str, *, handoff_root=None, base_ref=None):
        assert base_ref == "abc123def456"
        return ["docs/a.md"]

    monkeypatch.setattr(
        "src.business_services.run_orchestrator.collect_commit_paths",
        _collect,
    )
    run = RunModel(
        id=uuid4(),
        org="acme",
        repo="widget",
        status_type=RunStatusType.ACTIVE,
        initiative_id="INIT-GATEFLOW-006",
        wave_id="w1",
        created_at=datetime.now(UTC),
    )
    await orch._publish_stage_workspace_if_needed(
        MagicMock(),
        run=run,
        workspace_path=str(tmp_path),
        node_id="pre-implement",
        payload={
            "initiative_id": "INIT-GATEFLOW-006",
            "wave_id": "w1",
            "branch_slug": "forge-commit",
        },
    )
    forge.commit_paths_to_branch.assert_awaited()
    events.append_event.assert_awaited()
    event_arg = events.append_event.await_args.args[1]
    assert event_arg.event_type == "stage_commit"
    assert event_arg.payload["commit_sha"] == "deadbeef"


@pytest.mark.asyncio
async def test_closeout_walk_applies_done_then_stops_at_wave_signoff() -> None:
    """REQ-05: ground-spec pass → automated wave-done-action → STOP wave-signoff purpose."""
    from src.models.forge_types import ForgeActionType
    from src.models.handoff_models import HandoffEnvelope

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
    handoff_reader = MagicMock()
    handoff_reader.read_path = MagicMock(
        return_value=HandoffEnvelope(
            contract="sdd-delivery/v2",
            stage="ground-spec",
            outcome="pass",
            blockers=[],
            human_checkpoint=False,
        )
    )
    run_event_repo = MagicMock()
    run_event_repo.append_event = AsyncMock()
    stage_repo = MagicMock()
    stage_repo.create_stage = AsyncMock()
    forge_action = MagicMock()
    forge_action.apply_external_action = AsyncMock(
        return_value=MagicMock(
            pr_number=None,
            action=ForgeActionType.UPDATE_BOARD_STATUS,
            board_ticket=MagicMock(ticket_id="141", column="Done"),
        )
    )
    raw = _job_payload(event_type="api_trigger").model_dump()
    raw.pop("handoff", None)
    raw.update(_dispatch_plan(start_node="ground-spec", model_id="cursor/auto"))
    raw["head_ref"] = "feature/INIT-GATEFLOW-010-w3-closeout-done"
    raw["ticket_id"] = "141"
    forge_client = MagicMock()
    forge_client.ensure_branch_from_base = AsyncMock(return_value=True)
    forge_client.get_branch_tip_sha = AsyncMock(return_value="deadbeef")
    orchestrator = _build_orchestrator(
        trigger_router=_authorized_api_trigger(),
        cursor_agent_runner=cursor_agent_runner,
        handoff_reader=handoff_reader,
        stage_repository=stage_repo,
        run_event_repository=run_event_repo,
        forge_action_service=forge_action,
        forge_client=forge_client,
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
    assert cursor_agent_runner.run_skill.await_count == 1
    forge_action.apply_external_action.assert_awaited_once()
    apply_kwargs = forge_action.apply_external_action.await_args.kwargs
    assert apply_kwargs["node"].node_id == "wave-done-action"
    assert apply_kwargs["ticket_ref"] == "141"
    forge_client.ensure_branch_from_base.assert_not_awaited()

    forge_events = [
        call.args[1]
        for call in run_event_repo.append_event.await_args_list
        if call.args[1].event_type == "forge_executed"
    ]
    assert any(e.workflow_node == "wave-done-action" for e in forge_events)

    stopped_events = [
        call.args[1]
        for call in run_event_repo.append_event.await_args_list
        if call.args[1].event_type == "run_stopped"
    ]
    assert len(stopped_events) == 1
    assert stopped_events[0].workflow_node == "wave-signoff"
    assert stopped_events[0].payload.get("purpose") == "wave-signoff"


@pytest.mark.asyncio
async def test_closure_walk_purge_then_pr_action_stops_at_signoff_app() -> None:
    """REQ-15: purge-app → automated closure PR → STOP initiative-closure-signoff-app."""
    from src.models.forge_models import HandoffForgeDocument
    from src.models.forge_types import ForgeActionType
    from src.models.handoff_models import HandoffEnvelope

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
    handoff_reader = MagicMock()
    handoff_reader.read_path = MagicMock(
        return_value=HandoffEnvelope(
            contract="sdd-delivery/v2",
            stage="purge-initiative-artifacts-app",
            outcome="pass",
            blockers=[],
            human_checkpoint=False,
            forge=HandoffForgeDocument(
                action="open_draft_pr",
                head_ref="feature/INIT-GATEFLOW-010-w4-closure",
                base_ref="develop",
            ),
            signals={
                "pr_body": "## Initiative closure\n\nApp purge complete.",
                "initiative": "INIT-GATEFLOW-010",
            },
        )
    )
    run_event_repo = MagicMock()
    run_event_repo.append_event = AsyncMock()
    stage_repo = MagicMock()
    stage_repo.create_stage = AsyncMock()
    forge_action = MagicMock()
    forge_action.apply_external_action = AsyncMock(
        return_value=MagicMock(
            pr_number=160,
            action=ForgeActionType.OPEN_DRAFT_PR,
            board_ticket=None,
        )
    )
    raw = _job_payload(event_type="api_trigger").model_dump()
    raw.pop("handoff", None)
    raw.update(_dispatch_plan(start_node="purge-initiative-artifacts-app", model_id="cursor/auto"))
    raw.update(
        {
            "lane": "closure",
            "head_ref": "feature/INIT-GATEFLOW-010-w4-closure",
            "branch_slug": "w4-closure",
            "initiative_id": "INIT-GATEFLOW-010",
            "ticket_id": "137",
            "epic_ticket_id": "137",
            "epic_done_applied": True,
            "wave_ticket_ids": ["138", "139", "140", "141", "142"],
        }
    )
    forge_client = MagicMock()
    forge_client.ensure_branch_from_base = AsyncMock(return_value=True)
    forge_client.get_branch_tip_sha = AsyncMock(return_value="deadbeef")
    orchestrator = _build_orchestrator(
        trigger_router=_authorized_api_trigger(),
        cursor_agent_runner=cursor_agent_runner,
        handoff_reader=handoff_reader,
        stage_repository=stage_repo,
        run_event_repository=run_event_repo,
        forge_action_service=forge_action,
        forge_client=forge_client,
    )
    summary = await orchestrator.process_job(
        JobModel(
            id=uuid4(),
            status_type=JobStatusType.CLAIMED,
            payload=JobPayloadDocument.model_validate(raw),
            delivery_id="d-closure",
        )
    )
    assert summary.dispatched is True
    assert summary.terminal_status == RunStatusType.STOPPED.value
    assert cursor_agent_runner.run_skill.await_count == 1
    forge_action.apply_external_action.assert_awaited_once()
    apply_kwargs = forge_action.apply_external_action.await_args.kwargs
    assert apply_kwargs["node"].node_id == "initiative-closure-pr-action-app"

    stopped_events = [
        call.args[1]
        for call in run_event_repo.append_event.await_args_list
        if call.args[1].event_type == "run_stopped"
    ]
    assert len(stopped_events) == 1
    assert stopped_events[0].workflow_node == "initiative-closure-signoff-app"
    assert stopped_events[0].payload.get("purpose") == "initiative-closure-signoff-app"

    stages = [
        call.args[1].workflow_node
        for call in run_event_repo.append_event.await_args_list
        if call.args[1].event_type == "stage_started"
    ]
    assert "purge-initiative-artifacts-meta" not in stages


@pytest.mark.asyncio
async def test_closure_partial_failure_after_epic_done_records_req20() -> None:
    """REQ-20: forge failure after EPIC Done — partial_closure_failure, no complete claim."""
    from src.models.forge_models import HandoffForgeDocument
    from src.models.handoff_models import HandoffEnvelope

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
    handoff_reader = MagicMock()
    handoff_reader.read_path = MagicMock(
        return_value=HandoffEnvelope(
            contract="sdd-delivery/v2",
            stage="purge-initiative-artifacts-app",
            outcome="pass",
            blockers=[],
            human_checkpoint=False,
            forge=HandoffForgeDocument(
                action="open_draft_pr",
                title="Closure",
                body_path="docs/specification/reports/Purge-App-INIT-GATEFLOW-010.md",
                head_ref="feature/INIT-GATEFLOW-010-w4-closure",
                base_ref="develop",
            ),
        )
    )
    run_event_repo = MagicMock()
    run_event_repo.append_event = AsyncMock()
    stage_repo = MagicMock()
    stage_repo.create_stage = AsyncMock()
    forge_action = MagicMock()
    forge_action.apply_external_action = AsyncMock(side_effect=RuntimeError("draft PR failed"))
    raw = _job_payload(event_type="api_trigger").model_dump()
    raw.pop("handoff", None)
    raw.update(_dispatch_plan(start_node="purge-initiative-artifacts-app", model_id="cursor/auto"))
    raw.update(
        {
            "lane": "closure",
            "head_ref": "feature/INIT-GATEFLOW-010-w4-closure",
            "branch_slug": "w4-closure",
            "initiative_id": "INIT-GATEFLOW-010",
            "ticket_id": "137",
            "epic_done_applied": True,
        }
    )
    forge_client = MagicMock()
    forge_client.ensure_branch_from_base = AsyncMock(return_value=True)
    forge_client.get_branch_tip_sha = AsyncMock(return_value="deadbeef")
    orchestrator = _build_orchestrator(
        trigger_router=_authorized_api_trigger(),
        cursor_agent_runner=cursor_agent_runner,
        handoff_reader=handoff_reader,
        stage_repository=stage_repo,
        run_event_repository=run_event_repo,
        forge_action_service=forge_action,
        forge_client=forge_client,
    )
    summary = await orchestrator.process_job(
        JobModel(
            id=uuid4(),
            status_type=JobStatusType.CLAIMED,
            payload=JobPayloadDocument.model_validate(raw),
            delivery_id="d-closure-fail",
        )
    )
    assert summary.terminal_status == RunStatusType.FAILED.value
    stopped_events = [
        call.args[1]
        for call in run_event_repo.append_event.await_args_list
        if call.args[1].event_type == "run_stopped"
    ]
    assert len(stopped_events) == 1
    payload = stopped_events[0].payload
    assert payload.get("partial_closure_failure") is True
    assert payload.get("closure_complete_claim") is False
    assert payload.get("epic_done_applied") is True


def test_src_has_no_retired_checkpoint_transition_ids() -> None:
    """REQ-16 — runtime src must not hardcode retired pin checkpoint ids."""
    retired = ("gate-1", "gate-2", "wave-human-decision")
    root = Path("src")
    offenders: list[str] = []
    for path in root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for token in retired:
            if token in text:
                offenders.append(f"{path}:{token}")
    assert not offenders, f"retired checkpoint ids still present: {offenders}"


@pytest.mark.asyncio
async def test_omitted_workspace_unregistered_fails_without_cwd() -> None:
    """REQ-15 / FF-01: orchestrator must not fall back to Path.cwd()."""
    from src.models.control_plane_models import TriggerAuthorizationResult, TriggerContext

    trigger_router = MagicMock()
    trigger_router.authorize_and_check = AsyncMock(
        return_value=TriggerAuthorizationResult(
            authorized=True,
            context=TriggerContext(
                org="acme",
                repo="widget",
                event_type="api_trigger",
                delivery_id="d-run",
                trigger_label="",
                workspace_path=None,
            ),
            failures=[],
        )
    )
    orchestrator = _build_orchestrator(trigger_router=trigger_router)
    raw = _job_payload().model_dump()
    raw.pop("workspace_path", None)
    summary = await orchestrator.process_job(
        JobModel(
            id=uuid4(),
            status_type=JobStatusType.CLAIMED,
            payload=JobPayloadDocument.model_validate(raw),
            delivery_id="d-run",
        )
    )
    assert summary.dispatched is False
    assert summary.terminal_status == "failed"
    assert "Path.cwd()" in (summary.stop_reason or "")
    launchpad = orchestrator._launchpad_client
    assert isinstance(launchpad.sync_harness, AsyncMock)
    launchpad.sync_harness.assert_not_awaited()


@pytest.mark.asyncio
async def test_omitted_workspace_registered_resolves_via_client(tmp_path: Path) -> None:
    """REQ-10: omitted path + registered repo uses tenant git client."""
    from src.models.control_plane_models import TriggerAuthorizationResult, TriggerContext
    from src.models.tenant_git_workspace_models import (
        TenantWorkspaceCredential,
        WorkspaceResolveModeType,
        WorkspaceResolveResult,
    )

    resolved = str((tmp_path / "acme" / "widget").resolve())
    (tmp_path / "acme" / "widget").mkdir(parents=True)

    trigger_router = MagicMock()
    trigger_router.authorize_and_check = AsyncMock(
        return_value=TriggerAuthorizationResult(
            authorized=True,
            context=TriggerContext(
                org="acme",
                repo="widget",
                event_type="api_trigger",
                delivery_id="d-run",
                trigger_label="",
                workspace_path=None,
            ),
            failures=[],
        )
    )
    tenant_service = MagicMock()
    tenant_service.get_workspace_credential_for_repo = AsyncMock(
        return_value=TenantWorkspaceCredential(
            tenant_id=uuid4(),
            workspace_root=str(tmp_path),
            pat="pat",
            org="acme",
            repo="widget",
        )
    )
    git_client = MagicMock()
    git_client.resolve_workspace = AsyncMock(
        return_value=WorkspaceResolveResult(
            path=resolved,
            mode=WorkspaceResolveModeType.FETCHED,
        )
    )
    git_client.checkout_branch = AsyncMock()
    orchestrator = _build_orchestrator(
        trigger_router=trigger_router,
        tenant_service=tenant_service,
        tenant_git_workspace_client=git_client,
    )
    cursor = orchestrator._cursor_agent_runner
    cursor.run_skill = AsyncMock(
        return_value=AgentRunResult(
            runner="cursor",
            outcome=AgentRunOutcomeType.SUCCESS,
            error_message=None,
        )
    )
    raw = _job_payload().model_dump()
    raw.pop("workspace_path", None)
    await orchestrator.process_job(
        JobModel(
            id=uuid4(),
            status_type=JobStatusType.CLAIMED,
            payload=JobPayloadDocument.model_validate(raw),
            delivery_id="d-run",
        )
    )
    git_client.resolve_workspace.assert_awaited_once()
    git_client.checkout_branch.assert_awaited_once()
    checkout_kwargs = git_client.checkout_branch.await_args.kwargs
    assert checkout_kwargs["branch"] == "feature/INIT-GATEFLOW-008-w1-implement-lane"
    launchpad = orchestrator._launchpad_client
    assert isinstance(launchpad.sync_harness, AsyncMock)
    launchpad.sync_harness.assert_awaited()
    sync_call = launchpad.sync_harness.await_args
    assert sync_call is not None
    assert sync_call.args[0] == resolved


@pytest.mark.asyncio
async def test_resolve_branch_new_wave_calls_ensure_from_base() -> None:
    """REQ-16: missing remote head forks from live base tip."""
    forge_client = MagicMock()
    forge_client.get_branch_tip_sha = AsyncMock(side_effect=ValueError("missing"))
    forge_client.ensure_branch_from_base = AsyncMock(return_value=True)
    orch = _build_orchestrator(forge_client=forge_client)
    run = RunModel(
        id=uuid4(),
        org="acme",
        repo="widget",
        status_type=RunStatusType.ACTIVE,
        initiative_id="INIT-ACME-001",
        wave_id="W1",
        retry_counter=0,
        notify_pending=False,
    )
    head, mode = await orch.resolve_branch(
        org="acme",
        repo="widget",
        run=run,
        payload={
            "initiative_id": "INIT-ACME-001",
            "wave_id": "W1",
            "branch_slug": "branch-resolve",
            "base_branch": "develop",
        },
    )
    from src.models.pr_branch_naming import BranchResolveModeType

    assert head == "feature/INIT-ACME-001-w1-branch-resolve"
    assert mode is BranchResolveModeType.NEW_WAVE
    forge_client.ensure_branch_from_base.assert_awaited_once()
    kwargs = forge_client.ensure_branch_from_base.await_args.kwargs
    assert kwargs["branch"] == head
    assert kwargs["base"] == "develop"


@pytest.mark.asyncio
async def test_resolve_branch_continuation_reuses_without_ensure() -> None:
    """REQ-18: existing remote head → zero ensure_branch_from_base calls."""
    forge_client = MagicMock()
    forge_client.get_branch_tip_sha = AsyncMock(return_value="abc123")
    forge_client.ensure_branch_from_base = AsyncMock(return_value=True)
    orch = _build_orchestrator(forge_client=forge_client)
    run = RunModel(
        id=uuid4(),
        org="acme",
        repo="widget",
        status_type=RunStatusType.ACTIVE,
        initiative_id="INIT-ACME-001",
        wave_id="W1",
        retry_counter=0,
        notify_pending=False,
    )
    head, mode = await orch.resolve_branch(
        org="acme",
        repo="widget",
        run=run,
        payload={
            "initiative_id": "INIT-ACME-001",
            "wave_id": "W1",
            "branch_slug": "branch-resolve",
            "base_branch": "develop",
        },
    )
    from src.models.pr_branch_naming import BranchResolveModeType

    assert head == "feature/INIT-ACME-001-w1-branch-resolve"
    assert mode is BranchResolveModeType.CONTINUATION
    forge_client.ensure_branch_from_base.assert_not_awaited()
    forge_client.get_branch_tip_sha.assert_awaited()


@pytest.mark.asyncio
async def test_resolve_branch_explicit_head_missing_named_422_reason() -> None:
    """Continuation with head_ref missing on remote → named fail-closed reason."""
    forge_client = MagicMock()
    forge_client.get_branch_tip_sha = AsyncMock(side_effect=ValueError("404"))
    forge_client.ensure_branch_from_base = AsyncMock(return_value=True)
    orch = _build_orchestrator(forge_client=forge_client)
    run = RunModel(
        id=uuid4(),
        org="acme",
        repo="widget",
        status_type=RunStatusType.ACTIVE,
        initiative_id="INIT-ACME-001",
        wave_id="W1",
        retry_counter=0,
        notify_pending=False,
    )
    with pytest.raises(ValueError, match="continuation branch not found on remote"):
        await orch.resolve_branch(
            org="acme",
            repo="widget",
            run=run,
            payload={
                "initiative_id": "INIT-ACME-001",
                "wave_id": "W1",
                "branch_slug": "branch-resolve",
                "base_branch": "develop",
                "head_ref": "feature/INIT-ACME-001-w1-branch-resolve",
            },
        )
    forge_client.ensure_branch_from_base.assert_not_awaited()


@pytest.mark.asyncio
async def test_process_job_continuation_missing_head_fails_closed() -> None:
    """Job start with head_ref missing on remote fails (named 422 reason in stop_reason)."""
    from src.models.control_plane_models import TriggerAuthorizationResult, TriggerContext

    forge_client = MagicMock()
    forge_client.get_branch_tip_sha = AsyncMock(side_effect=ValueError("404"))
    forge_client.ensure_branch_from_base = AsyncMock(return_value=True)

    trigger_router = MagicMock()
    trigger_router.authorize_and_check = AsyncMock(
        return_value=TriggerAuthorizationResult(
            authorized=True,
            context=TriggerContext(
                org="acme",
                repo="widget",
                event_type="api_trigger",
                delivery_id="d-run",
                trigger_label="",
                workspace_path=str(Path.cwd()),
            ),
            failures=[],
        )
    )
    orch = _build_orchestrator(trigger_router=trigger_router, forge_client=forge_client)
    raw = _job_payload(
        event_type="api_trigger",
        pr_number=None,
        initiative_id="INIT-ACME-001",
        wave_id="W1",
        branch_slug="gone",
        base_branch="develop",
        head_ref="feature/INIT-ACME-001-w1-gone",
        **_dispatch_plan(start_node="ground-spec", model_id="cursor/auto"),
    ).model_dump()
    summary = await orch.process_job(
        JobModel(
            id=uuid4(),
            status_type=JobStatusType.CLAIMED,
            payload=JobPayloadDocument.model_validate(raw),
            delivery_id="d-run",
        )
    )
    assert summary.dispatched is False
    assert summary.terminal_status == "failed"
    assert "continuation branch not found on remote" in (summary.stop_reason or "")
    forge_client.ensure_branch_from_base.assert_not_awaited()
