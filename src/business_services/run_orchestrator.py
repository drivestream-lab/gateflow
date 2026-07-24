"""RunOrchestrator — job → trigger → policy → PR-at-start → dispatch (FR-16/19)."""

import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Optional
from uuid import UUID

from injector import inject
from sqlalchemy.ext.asyncio import AsyncSession

from src.business_services.base_business_service import BaseBusinessService
from src.business_services.handoff_reader import HandoffReader
from src.business_services.metrics_emitter import MetricsEmitter
from src.business_services.node_model_resolver import resolve_node_dispatch
from src.business_services.notifier import Notifier
from src.business_services.policy_engine import PolicyEngine
from src.business_services.stage_tool_resolver import StageToolResolver
from src.business_services.trigger_router import TriggerRouter
from src.database.postgres.repository.run_store_repository import (
    RunEventRepository,
    RunRepository,
    StageRepository,
)
from src.infra_services.cursor_agent_runner import CursorAgentRunner
from src.infra_services.forge_client import ForgeClient
from src.infra_services.launchpad_client import LaunchpadClient
from src.infra_services.postgres_service import PostgresService
from src.models.control_plane_models import RunEventComment, RunProcessSummary
from src.models.handoff_models import HandoffEnvelope
from src.models.policy_types import PolicyDecisionType, RunEventNameType
from src.models.programme_config_models import ProgrammeConfig
from src.models.run_store_models import (
    JobModel,
    RunCreate,
    RunEventCreate,
    RunModel,
    RunUpdate,
    StageCreate,
)
from src.models.run_store_types import RunOutcomeType, RunStatusType


class RunOrchestrator(BaseBusinessService):
    """Process claimed jobs through trigger, policy, PR-at-start, and agent dispatch."""

    @inject
    def __init__(
        self,
        postgres_service: PostgresService,
        trigger_router: TriggerRouter,
        policy_engine: PolicyEngine,
        handoff_reader: HandoffReader,
        notifier: Notifier,
        metrics_emitter: MetricsEmitter,
        stage_tool_resolver: StageToolResolver,
        launchpad_client: LaunchpadClient,
        cursor_agent_runner: CursorAgentRunner,
        forge_client: ForgeClient,
        run_repository: RunRepository,
        run_event_repository: RunEventRepository,
        stage_repository: StageRepository,
    ) -> None:
        super().__init__()
        self._postgres_service = postgres_service
        self._trigger_router = trigger_router
        self._policy_engine = policy_engine
        self._handoff_reader = handoff_reader
        self._notifier = notifier
        self._metrics_emitter = metrics_emitter
        self._stage_tool_resolver = stage_tool_resolver
        self._launchpad_client = launchpad_client
        self._cursor_agent_runner = cursor_agent_runner
        self._forge_client = forge_client
        self._run_repository = run_repository
        self._run_event_repository = run_event_repository
        self._stage_repository = stage_repository

    async def process_job(self, job: JobModel) -> RunProcessSummary:
        """Run trigger → handoff → policy → PR-at-start → optional dispatch."""
        programme_config = ProgrammeConfig.get_instance()
        payload = job.payload.model_dump()
        event_type = job.payload.event_type
        delivery_id = job.payload.delivery_id

        async with self._postgres_service.transaction() as session:
            auth = await self._trigger_router.authorize_and_check(
                session,
                event_type=event_type,
                delivery_id=delivery_id,
                payload=payload,
                programme_config=programme_config,
            )
            if not auth.authorized or auth.context is None:
                failure = auth.failures[0] if auth.failures else None
                reason = failure.reason if failure else "Trigger authorization failed"
                ctx = auth.context
                if ctx is not None:
                    issue_ref = ctx.pr_number or ctx.issue_number
                    notify_pending = await self._notifier.notify_precondition_failure(
                        ctx.org,
                        ctx.repo,
                        issue_ref,
                        reason,
                    )
                    if notify_pending:
                        self.logger.warning(
                            "Precondition failure notify_pending",
                            delivery_id=delivery_id,
                            reason=reason,
                        )
                return RunProcessSummary(
                    terminal_status="not_dispatched",
                    stop_reason=reason,
                    dispatched=False,
                )

            context = auth.context
            existing_run_id = payload.get("run_id")
            if existing_run_id:
                run = await self._run_repository.get_run(session, UUID(str(existing_run_id)))
                if run is None:
                    return RunProcessSummary(
                        terminal_status="not_dispatched",
                        stop_reason=f"Pre-created run {existing_run_id} not found",
                        dispatched=False,
                    )
            else:
                run = await self._run_repository.create_run(
                    session,
                    RunCreate(
                        org=context.org,
                        repo=context.repo,
                        status_type=RunStatusType.ACTIVE,
                        pr_number=context.pr_number,
                        issue_number=context.issue_number,
                        initiative_id=context.initiative_id,
                    ),
                )
            if run.id is None:
                raise RuntimeError("Created run missing id")
            run_id = run.id

            notify_pending = False
            run, notify_pending = await self._ensure_run_pr(
                session,
                run,
                programme_config=programme_config,
                payload=payload,
                notify_pending=notify_pending,
            )
            issue_ref = run.pr_number or context.pr_number or context.issue_number

            try:
                handoff = self._resolve_handoff(payload, context.workspace_path, programme_config)
            except ValueError as exc:
                return await self._finalize_run(
                    session,
                    run,
                    status_type=RunStatusType.FAILED,
                    outcome_type=RunOutcomeType.FAILED,
                    stop_reason=str(exc),
                    workflow_node=None,
                    dispatched=False,
                    notify_pending=notify_pending,
                    issue_ref=issue_ref,
                    org=context.org,
                    repo=context.repo,
                )

            decision = self._policy_engine.evaluate_dispatch(
                handoff=handoff,
                trigger=context,
                programme_config=programme_config,
                retry_counter=run.retry_counter,
            )

            if decision.decision in {PolicyDecisionType.STOP, PolicyDecisionType.BLOCK}:
                outcome = (
                    RunOutcomeType.BLOCKED
                    if decision.decision == PolicyDecisionType.BLOCK
                    else RunOutcomeType.STOPPED
                )
                return await self._finalize_run(
                    session,
                    run,
                    status_type=RunStatusType.STOPPED,
                    outcome_type=outcome,
                    stop_reason=decision.block_reason or decision.decision.value,
                    workflow_node=decision.next_node.node_id if decision.next_node else None,
                    dispatched=False,
                    notify_pending=notify_pending,
                    issue_ref=issue_ref,
                    org=context.org,
                    repo=context.repo,
                )

            assert decision.next_node is not None
            next_node = decision.next_node
            started_at = datetime.now(UTC)
            started_notify = await self._post_run_event(
                context.org,
                context.repo,
                issue_ref,
                run_id,
                next_node.node_id,
                RunEventNameType.STAGE_STARTED,
                outcome=None,
                duration_ms=None,
                timestamp=started_at,
            )
            notify_pending = notify_pending or started_notify

            workspace_path = context.workspace_path or str(Path.cwd())
            await self._launchpad_client.sync_harness(workspace_path)
            _tool_context = self._stage_tool_resolver.resolve(
                next_node.node_id,
                programme_config=programme_config,
            )
            _ = _tool_context

            try:
                resolved = resolve_node_dispatch(programme_config, next_node.node_id)
            except ValueError as exc:
                return await self._finalize_run(
                    session,
                    run,
                    status_type=RunStatusType.FAILED,
                    outcome_type=RunOutcomeType.FAILED,
                    stop_reason=str(exc),
                    workflow_node=next_node.node_id,
                    dispatched=False,
                    notify_pending=notify_pending,
                    issue_ref=issue_ref,
                    org=context.org,
                    repo=context.repo,
                )

            if resolved.runner != "cursor":
                return await self._finalize_run(
                    session,
                    run,
                    status_type=RunStatusType.FAILED,
                    outcome_type=RunOutcomeType.FAILED,
                    stop_reason=(
                        f"No AgentRunner wired for adapter {resolved.runner!r} "
                        f"(W1 Cursor path only)"
                    ),
                    workflow_node=next_node.node_id,
                    dispatched=False,
                    notify_pending=notify_pending,
                    issue_ref=issue_ref,
                    org=context.org,
                    repo=context.repo,
                )

            prompt_context: dict[str, Any] = {
                "initiative_id": context.initiative_id or payload.get("initiative_id"),
                "handoff_stage": handoff.stage,
                "handoff_outcome": handoff.outcome,
            }
            if isinstance(payload.get("prompt_context"), dict):
                prompt_context.update(payload["prompt_context"])

            t0 = time.monotonic()
            agent_result = await self._cursor_agent_runner.run_skill(
                workspace_path=workspace_path,
                skill_id=next_node.node_id,
                prompt_context=prompt_context,
                model_profile=resolved.model_profile,
                runner=resolved.runner,
                model_id=resolved.model_id,
                model_provider=resolved.model_provider,
            )
            duration_ms = int((time.monotonic() - t0) * 1000)

            if agent_result.outcome.value != "success":
                return await self._finalize_run(
                    session,
                    run,
                    status_type=RunStatusType.FAILED,
                    outcome_type=RunOutcomeType.FAILED,
                    stop_reason=agent_result.error_message or "Agent run failed",
                    workflow_node=next_node.node_id,
                    dispatched=True,
                    notify_pending=notify_pending,
                    issue_ref=issue_ref,
                    org=context.org,
                    repo=context.repo,
                )

            await self._metrics_emitter.record_stage_duration(
                session,
                run_id,
                next_node.node_id,
                duration_ms,
                outcome="success",
                runner=resolved.runner,
                model_id=resolved.model_id,
                model_profile=resolved.model_profile,
            )
            await self._stage_repository.create_stage(
                session,
                StageCreate(
                    run_id=run_id,
                    workflow_node=next_node.node_id,
                    outcome_type=RunOutcomeType.SUCCESS,
                    started_at=started_at,
                    ended_at=datetime.now(UTC),
                    runner=resolved.runner,
                    model_profile=resolved.model_profile,
                    model_id=resolved.model_id,
                    model_provider=resolved.model_provider,
                ),
            )
            completed_notify = await self._post_run_event(
                context.org,
                context.repo,
                issue_ref,
                run_id,
                next_node.node_id,
                RunEventNameType.STAGE_COMPLETED,
                outcome=RunOutcomeType.SUCCESS.value,
                duration_ms=duration_ms,
                timestamp=datetime.now(UTC),
            )
            notify_pending = notify_pending or completed_notify

            updated = await self._run_repository.update_run(
                session,
                run_id,
                RunUpdate(
                    status_type=RunStatusType.COMPLETED,
                    outcome_type=RunOutcomeType.SUCCESS,
                    workflow_node=next_node.node_id,
                    notify_pending=notify_pending,
                ),
            )
            if updated is None:
                raise RuntimeError(f"Run {run_id} missing after dispatch success")

            self.logger.info(
                "Run dispatch completed",
                run_id=str(run_id),
                workflow_node=next_node.node_id,
                runner=resolved.runner,
                model_profile=resolved.model_profile,
                duration_ms=duration_ms,
            )
            return RunProcessSummary(
                run_id=run_id,
                terminal_status=RunStatusType.COMPLETED.value,
                dispatched=True,
            )

    async def _ensure_run_pr(
        self,
        session: AsyncSession,
        run: RunModel,
        *,
        programme_config: ProgrammeConfig,
        payload: dict[str, Any],
        notify_pending: bool,
    ) -> tuple[RunModel, bool]:
        """Open or update the run PR before orchestrated stages (FR-19)."""
        if run.id is None:
            raise RuntimeError("Run missing id before PR-at-start")
        if run.pr_number is not None:
            return run, notify_pending

        run_id_str = str(run.id)
        run_id_short = run_id_str.replace("-", "")[:8]
        initiative_id = run.initiative_id or str(payload.get("initiative_id") or "unknown")
        wave_id = run.wave_id or str(payload.get("wave_id") or "unknown")
        template_vars = {
            "initiative_id": initiative_id,
            "wave_id": wave_id,
            "run_id": run_id_str,
            "run_id_short": run_id_short,
        }
        pr_cfg = programme_config.pr
        title = pr_cfg.title_template.format(**template_vars)
        body = pr_cfg.body_template.format(**template_vars)
        head = f"{pr_cfg.branch_prefix}{run_id_short}"
        try:
            pr_number = await self._forge_client.create_or_update_pull_request(
                run.org,
                run.repo,
                title=title,
                body=body,
                head=head,
                base=pr_cfg.base_branch,
            )
        except Exception as exc:
            self.logger.error(
                "PR open/update failed at run start",
                run_id=run_id_str,
                error=str(exc),
                exc_info=True,
            )
            updated = await self._run_repository.update_run(
                session,
                run.id,
                RunUpdate(notify_pending=True),
            )
            return (updated or run), True

        updated = await self._run_repository.update_run(
            session,
            run.id,
            RunUpdate(pr_number=pr_number),
        )
        if updated is None:
            raise RuntimeError(f"Run {run.id} missing after PR assign")
        self.logger.info(
            "Run PR ensured at start",
            run_id=run_id_str,
            pr_number=pr_number,
            head=head,
        )
        return updated, notify_pending

    def _resolve_handoff(
        self,
        payload: dict[str, Any],
        workspace_path: Optional[str],
        programme_config: ProgrammeConfig,
    ) -> HandoffEnvelope:
        handoff_raw = payload.get("handoff")
        if isinstance(handoff_raw, dict):
            return HandoffEnvelope.model_validate(handoff_raw)
        if workspace_path:
            return self._handoff_reader.find_latest_handoff(
                Path(workspace_path),
                programme_config=programme_config,
            )
        raise ValueError("Handoff required — set workspace_path or payload.handoff for tests")

    async def _post_run_event(
        self,
        org: str,
        repo: str,
        issue_ref: Optional[int],
        run_id: UUID,
        workflow_node: Optional[str],
        event: RunEventNameType,
        outcome: Optional[str],
        duration_ms: Optional[int],
        timestamp: datetime,
    ) -> bool:
        if issue_ref is None:
            return False
        comment = RunEventComment(
            run_id=run_id,
            workflow_node=workflow_node,
            event=event,
            outcome=outcome,
            duration_ms=duration_ms,
            timestamp=timestamp,
        )
        return await self._notifier.post_run_event_comment(org, repo, issue_ref, comment)

    async def _finalize_run(
        self,
        session: AsyncSession,
        run: RunModel,
        *,
        status_type: RunStatusType,
        outcome_type: RunOutcomeType,
        stop_reason: str,
        workflow_node: Optional[str],
        dispatched: bool,
        notify_pending: bool = False,
        issue_ref: Optional[int] = None,
        org: Optional[str] = None,
        repo: Optional[str] = None,
    ) -> RunProcessSummary:
        if run.id is None:
            raise RuntimeError("Run missing id during finalize")

        await self._run_event_repository.append_event(
            session,
            RunEventCreate(
                run_id=run.id,
                event_type="run_stopped",
                workflow_node=workflow_node,
                outcome_type=outcome_type,
                payload={"stop_reason": stop_reason, "event_type": "run_stopped"},
            ),
        )

        issue_number = issue_ref if issue_ref is not None else (run.pr_number or run.issue_number)
        org_name = org or run.org
        repo_name = repo or run.repo
        if issue_number is not None:
            stopped_notify = await self._post_run_event(
                org_name,
                repo_name,
                issue_number,
                run.id,
                workflow_node,
                RunEventNameType.RUN_STOPPED,
                outcome=outcome_type.value,
                duration_ms=None,
                timestamp=datetime.now(UTC),
            )
            notify_pending = notify_pending or stopped_notify

        await self._run_repository.update_run(
            session,
            run.id,
            RunUpdate(
                status_type=status_type,
                outcome_type=outcome_type,
                workflow_node=workflow_node,
                notify_pending=notify_pending,
            ),
        )
        self.logger.info(
            "Run finalized",
            run_id=str(run.id),
            status_type=status_type.value,
            outcome_type=outcome_type.value,
            stop_reason=stop_reason,
            dispatched=dispatched,
        )
        return RunProcessSummary(
            run_id=run.id,
            terminal_status=status_type.value,
            stop_reason=stop_reason,
            dispatched=dispatched,
        )


def get_run_orchestrator() -> RunOrchestrator:
    from src.di.dependency_container import provide_service

    return provide_service(RunOrchestrator)
