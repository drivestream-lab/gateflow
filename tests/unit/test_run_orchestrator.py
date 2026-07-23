"""Unit tests for RunOrchestrator branches (W1)."""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.business_services.run_orchestrator import RunOrchestrator
from src.configs.programme_config_loader import load_programme_config
from src.models.control_plane_models import AgentRunResult
from src.models.policy_types import AgentRunOutcomeType, PolicyDecisionType
from src.models.programme_config_models import ProgrammeConfig
from src.models.run_store_models import JobModel, JobPayloadDocument, RunModel
from src.models.run_store_types import JobStatusType, RunStatusType


@pytest.fixture(autouse=True)
def _programme_config() -> ProgrammeConfig:
    ProgrammeConfig.reset_instance()
    return load_programme_config(Path("config/programme.yaml"))


def _dispatch_handoff() -> dict[str, object]:
    return {
        "contract": "sdd-delivery/v2",
        "stage": "board-seed",
        "outcome": "pass",
        "blockers": [],
        "human_checkpoint": False,
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
        "handoff": _dispatch_handoff(),
        "workspace_path": str(Path.cwd()),
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
    run_repo = MagicMock()
    run_repo.create_run = AsyncMock(
        return_value=RunModel(
            id=run_id,
            org="acme",
            repo="widget",
            status_type=RunStatusType.ACTIVE,
            pr_number=7,
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
            pr_number=7,
            retry_counter=0,
            notify_pending=update.notify_pending or False,
        )
    )

    trigger_router = MagicMock()
    policy_engine = MagicMock()
    handoff_reader = MagicMock()
    notifier = MagicMock()
    notifier.notify_precondition_failure = AsyncMock(return_value=False)
    notifier.post_run_event_comment = AsyncMock(return_value=False)
    metrics_emitter = MagicMock()
    metrics_emitter.record_stage_duration = AsyncMock()
    stage_tool_resolver = MagicMock()
    stage_tool_resolver.resolve.return_value = MagicMock(slots={})
    launchpad_client = MagicMock()
    launchpad_client.sync_harness = AsyncMock()
    cursor_agent_runner = MagicMock()
    run_event_repo = MagicMock()
    run_event_repo.append_event = AsyncMock()
    stage_repo = MagicMock()
    stage_repo.create_stage = AsyncMock()

    defaults = {
        "postgres_service": postgres,
        "trigger_router": trigger_router,
        "policy_engine": policy_engine,
        "handoff_reader": handoff_reader,
        "notifier": notifier,
        "metrics_emitter": metrics_emitter,
        "stage_tool_resolver": stage_tool_resolver,
        "launchpad_client": launchpad_client,
        "cursor_agent_runner": cursor_agent_runner,
        "run_repository": run_repo,
        "run_event_repository": run_event_repo,
        "stage_repository": stage_repo,
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
async def test_stop_path_on_human_checkpoint() -> None:
    from src.models.control_plane_models import (
        PolicyDecision,
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
            ),
            failures=[],
        )
    )
    policy_engine = MagicMock()
    policy_engine.evaluate_dispatch = MagicMock(
        return_value=PolicyDecision(
            decision=PolicyDecisionType.STOP,
            block_reason="handoff.human_checkpoint is true",
        )
    )
    orchestrator = _build_orchestrator(
        trigger_router=trigger_router,
        policy_engine=policy_engine,
    )
    job = JobModel(
        id=uuid4(),
        status_type=JobStatusType.CLAIMED,
        payload=_job_payload(
            handoff={
                **_dispatch_handoff(),
                "human_checkpoint": True,
            }
        ),
        delivery_id="d-run",
    )
    summary = await orchestrator.process_job(job)
    assert summary.dispatched is False
    assert summary.run_id is not None
    assert summary.terminal_status == RunStatusType.STOPPED.value


@pytest.mark.asyncio
async def test_agent_failure_marks_run_failed() -> None:
    from src.models.control_plane_models import (
        PolicyDecision,
        TriggerAuthorizationResult,
        TriggerContext,
    )
    from src.models.handoff_models import ResolvedWorkflowNode

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
    policy_engine = MagicMock()
    policy_engine.evaluate_dispatch = MagicMock(
        return_value=PolicyDecision(
            decision=PolicyDecisionType.DISPATCH,
            next_node=ResolvedWorkflowNode(
                node_id="pre-implement",
                node_type="skill",
                dispatch="orchestrated",
            ),
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
    orchestrator = _build_orchestrator(
        trigger_router=trigger_router,
        policy_engine=policy_engine,
        cursor_agent_runner=cursor_agent_runner,
    )
    summary = await orchestrator.process_job(
        JobModel(
            id=uuid4(),
            status_type=JobStatusType.CLAIMED,
            payload=_job_payload(),
            delivery_id="d-run",
        )
    )
    assert summary.dispatched is True
    assert summary.terminal_status == RunStatusType.FAILED.value
    assert summary.stop_reason == "forced"
