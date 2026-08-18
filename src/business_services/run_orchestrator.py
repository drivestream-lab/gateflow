"""RunOrchestrator — Enter-at + pin-driven walker until gate (FR-15/16/19)."""

import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Optional
from uuid import UUID

from injector import inject
from sqlalchemy.ext.asyncio import AsyncSession

from src.business_services.base_business_service import BaseBusinessService
from src.business_services.forge_action_service import ForgeActionService
from src.business_services.handoff_reader import HandoffReader
from src.business_services.learning_ingest_service import (
    LEARNING_EXTRACT_NODE,
    LearningIngestService,
)
from src.business_services.metrics_emitter import MetricsEmitter
from src.business_services.node_model_resolver import resolve_node_dispatch
from src.business_services.notifier import Notifier
from src.business_services.policy_engine import PolicyEngine
from src.business_services.prompt_resolver import PromptResolver
from src.business_services.tenant_service import TenantService
from src.business_services.trigger_router import TriggerRouter
from src.business_services.workflow_engine import WorkflowEngine
from src.business_services.workspace_commit_paths import collect_commit_paths
from src.configs.orchestration_settings import OrchestrationSettings
from src.database.postgres.repository.platform_agent_catalogue_repository import (
    PlatformAgentCatalogueRepository,
)
from src.database.postgres.repository.run_store_repository import (
    RunEventRepository,
    RunRepository,
    StageRepository,
)
from src.exceptions.app_exceptions import UnprocessableEntityError, ValidationError
from src.infra_services.cursor_agent_runner import CursorAgentRunner
from src.infra_services.forge_client import ForgeClientFactory
from src.infra_services.launchpad_client import (
    HarnessReadinessError,
    LaunchpadClient,
)
from src.infra_services.launchpad_status_client import (
    LaunchpadStatusClient,
    LaunchpadStatusError,
)
from src.infra_services.postgres_service import PostgresService
from src.infra_services.tenant_git_workspace_client import (
    TenantGitWorkspaceClient,
    TenantGitWorkspaceError,
)
from src.models.control_plane_models import RunEventComment, RunProcessSummary
from src.models.dispatch_plan_models import DispatchPlan, ResolvedNodeDispatch
from src.models.forge_models import merge_pin_and_handoff_forge
from src.models.forge_types import CommitWorkspaceModeType
from src.models.handoff_models import HandoffEnvelope, ResolvedWorkflowNode
from src.models.programme_readiness_models import ReadinessSourceType
from src.models.policy_types import AgentRunOutcomeType, PolicyDecisionType, RunEventNameType
from src.models.pr_branch_naming import (
    BranchResolveModeType,
    branch_slug_from_head_ref,
    build_closure_head_branch,
    build_spec_head_branch,
    build_wave_head_branch,
    validate_base_branch,
)
from src.models.prompt_package_models import BoundPromptInputs, PromptResolveError
from src.models.run_store_models import (
    JobModel,
    RunCreate,
    RunEventCreate,
    RunModel,
    RunUpdate,
    StageCreate,
)
from src.models.run_store_types import RunOutcomeType, RunStatusType

# REQ-15 — eng closure walk must never dispatch PM/meta purge nodes.
_CLOSURE_META_FORBIDDEN_NODES = frozenset(
    {
        "purge-initiative-artifacts-meta",
        "initiative-closure-pr-action-meta",
        "initiative-closure-signoff-meta",
    }
)


class RunOrchestrator(BaseBusinessService):
    """Process jobs: trigger → ensure branch → Enter-at → walk pin until gate."""

    @inject
    def __init__(
        self,
        postgres_service: PostgresService,
        trigger_router: TriggerRouter,
        policy_engine: PolicyEngine,
        workflow_engine: WorkflowEngine,
        handoff_reader: HandoffReader,
        notifier: Notifier,
        metrics_emitter: MetricsEmitter,
        launchpad_client: LaunchpadClient,
        launchpad_status_client: LaunchpadStatusClient,
        cursor_agent_runner: CursorAgentRunner,
        forge_client_factory: ForgeClientFactory,
        forge_action_service: ForgeActionService,
        run_repository: RunRepository,
        run_event_repository: RunEventRepository,
        stage_repository: StageRepository,
        prompt_resolver: PromptResolver,
        learning_ingest_service: LearningIngestService,
        tenant_service: TenantService,
        tenant_git_workspace_client: TenantGitWorkspaceClient,
        catalogue_repository: PlatformAgentCatalogueRepository,
    ) -> None:
        super().__init__()
        self._postgres_service = postgres_service
        self._trigger_router = trigger_router
        self._policy_engine = policy_engine
        self._workflow_engine = workflow_engine
        self._handoff_reader = handoff_reader
        self._learning_ingest_service = learning_ingest_service
        self._notifier = notifier
        self._metrics_emitter = metrics_emitter
        self._launchpad_client = launchpad_client
        self._launchpad_status_client = launchpad_status_client
        self._cursor_agent_runner = cursor_agent_runner
        self._forge_client_factory = forge_client_factory
        self._forge_action_service = forge_action_service
        self._run_repository = run_repository
        self._run_event_repository = run_event_repository
        self._stage_repository = stage_repository
        self._prompt_resolver = prompt_resolver
        self._tenant_service = tenant_service
        self._tenant_git_workspace_client = tenant_git_workspace_client
        self._catalogue_repository = catalogue_repository
        self._orchestration = OrchestrationSettings.get_instance()

    async def process_job(self, job: JobModel) -> RunProcessSummary:
        """Authorize, ensure branch, Enter-at, then hop until STOP/BLOCK/fail."""
        payload = job.payload.model_dump()
        event_type = job.payload.event_type
        delivery_id = job.payload.delivery_id

        async with self._postgres_service.transaction() as session:
            auth = await self._trigger_router.authorize_and_check(
                session,
                event_type=event_type,
                delivery_id=delivery_id,
                payload=payload,
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
                        tenant_id=(
                            await self._require_tenant_id_for_repo(
                                org=context.org, repo=context.repo
                            )
                        ),
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
            resolved_head: Optional[str] = None
            try:
                run, notify_pending, resolved_head = await self._ensure_run_branch(
                    session,
                    run,
                    payload=payload,
                    notify_pending=notify_pending,
                )
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
                    issue_ref=run.pr_number or context.pr_number or context.issue_number,
                    org=context.org,
                    repo=context.repo,
                )
            issue_ref = run.pr_number or context.pr_number or context.issue_number

            start_node_id = payload.get("start_node")
            dispatch_plan_raw = payload.get("dispatch_plan")
            if not start_node_id or not isinstance(dispatch_plan_raw, dict):
                return await self._finalize_run(
                    session,
                    run,
                    status_type=RunStatusType.FAILED,
                    outcome_type=RunOutcomeType.FAILED,
                    stop_reason=(
                        "Enter-at requires start_node and dispatch_plan on the job payload"
                    ),
                    workflow_node=None,
                    dispatched=False,
                    notify_pending=notify_pending,
                    issue_ref=issue_ref,
                    org=context.org,
                    repo=context.repo,
                )

            try:
                next_node = self._workflow_engine.require_orchestrated_skill(str(start_node_id))
                dispatch_plan = DispatchPlan.model_validate(dispatch_plan_raw)
            except ValueError as exc:
                return await self._finalize_run(
                    session,
                    run,
                    status_type=RunStatusType.FAILED,
                    outcome_type=RunOutcomeType.FAILED,
                    stop_reason=str(exc),
                    workflow_node=str(start_node_id),
                    dispatched=False,
                    notify_pending=notify_pending,
                    issue_ref=issue_ref,
                    org=context.org,
                    repo=context.repo,
                )

            try:
                workspace_path, tenant_bound = await self._resolve_job_workspace_path(
                    org=context.org,
                    repo=context.repo,
                    workspace_path=context.workspace_path,
                )
                if tenant_bound and resolved_head:
                    await self._tenant_git_workspace_client.checkout_branch(
                        workspace_path,
                        branch=resolved_head,
                        org=context.org,
                        repo=context.repo,
                    )
            except (ValueError, UnprocessableEntityError, TenantGitWorkspaceError) as exc:
                reason = str(exc)
                if isinstance(exc, TenantGitWorkspaceError):
                    reason = f"{exc.reason}: {exc}"
                return await self._finalize_run(
                    session,
                    run,
                    status_type=RunStatusType.FAILED,
                    outcome_type=RunOutcomeType.FAILED,
                    stop_reason=reason,
                    workflow_node=str(start_node_id),
                    dispatched=False,
                    notify_pending=notify_pending,
                    issue_ref=issue_ref,
                    org=context.org,
                    repo=context.repo,
                )
            try:
                await self._ensure_harness_ready(
                    org=context.org,
                    repo=context.repo,
                    workspace_path=workspace_path,
                    force=bool(payload.get("force_harness_recheck")),
                )
            except (FileNotFoundError, HarnessReadinessError, UnprocessableEntityError) as exc:
                reason = str(exc)
                if isinstance(exc, HarnessReadinessError):
                    reason = f"{exc.reason}: missing={','.join(exc.missing)}"
                return await self._finalize_run(
                    session,
                    run,
                    status_type=RunStatusType.FAILED,
                    outcome_type=RunOutcomeType.FAILED,
                    stop_reason=reason,
                    workflow_node=str(start_node_id),
                    dispatched=False,
                    notify_pending=notify_pending,
                    issue_ref=issue_ref,
                    org=context.org,
                    repo=context.repo,
                )

            dispatched_any = False
            hop_count = 0
            retry_counter = int(run.retry_counter or 0)
            last_node_id = next_node.node_id

            while True:
                hop_count += 1
                if hop_count > self._orchestration.max_orchestrated_hops:
                    return await self._finalize_run(
                        session,
                        run,
                        status_type=RunStatusType.FAILED,
                        outcome_type=RunOutcomeType.FAILED,
                        stop_reason=(
                            f"Max orchestrated hops exceeded "
                            f"(GATEFLOW_MAX_ORCHESTRATED_HOPS="
                            f"{self._orchestration.max_orchestrated_hops})"
                        ),
                        workflow_node=last_node_id,
                        dispatched=dispatched_any,
                        notify_pending=notify_pending,
                        issue_ref=issue_ref,
                        org=context.org,
                        repo=context.repo,
                    )

                try:
                    resolved = resolve_node_dispatch(dispatch_plan, next_node.node_id)
                except ValueError as exc:
                    return await self._finalize_run(
                        session,
                        run,
                        status_type=RunStatusType.FAILED,
                        outcome_type=RunOutcomeType.FAILED,
                        stop_reason=str(exc),
                        workflow_node=next_node.node_id,
                        dispatched=dispatched_any,
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
                            f"(Cursor path only)"
                        ),
                        workflow_node=next_node.node_id,
                        dispatched=dispatched_any,
                        notify_pending=notify_pending,
                        issue_ref=issue_ref,
                        org=context.org,
                        repo=context.repo,
                    )

                stage_summary = await self._run_orchestrated_stage(
                    session,
                    run=run,
                    run_id=run_id,
                    context_org=context.org,
                    context_repo=context.repo,
                    issue_ref=issue_ref,
                    next_node=next_node,
                    resolved=resolved,
                    workspace_path=workspace_path,
                    payload=payload,
                    initiative_id=context.initiative_id,
                )
                notify_pending = notify_pending or stage_summary["notify_pending"]
                dispatched_any = True
                last_node_id = next_node.node_id

                if not stage_summary["success"]:
                    return await self._finalize_run(
                        session,
                        run,
                        status_type=RunStatusType.FAILED,
                        outcome_type=RunOutcomeType.FAILED,
                        stop_reason=stage_summary["stop_reason"] or "Agent run failed",
                        workflow_node=next_node.node_id,
                        dispatched=True,
                        notify_pending=notify_pending,
                        issue_ref=issue_ref,
                        org=context.org,
                        repo=context.repo,
                        job_payload=payload,
                    )

                try:
                    await self._publish_stage_workspace_if_needed(
                        session,
                        run=run,
                        workspace_path=workspace_path,
                        node_id=next_node.node_id,
                        payload=payload,
                    )
                except ValueError as exc:
                    return await self._finalize_run(
                        session,
                        run,
                        status_type=RunStatusType.FAILED,
                        outcome_type=RunOutcomeType.FAILED,
                        stop_reason=str(exc),
                        workflow_node=next_node.node_id,
                        dispatched=True,
                        notify_pending=notify_pending,
                        issue_ref=issue_ref,
                        org=context.org,
                        repo=context.repo,
                    )

                try:
                    stored_path = stage_summary.get("handoff_path") or (
                        str(run.handoff_path).strip() if run.handoff_path else ""
                    )
                    handoff = stage_summary.get("handoff")
                    if handoff is None:
                        handoff = self._ingest_handoff_after_stage(
                            handoff_path=str(stored_path),
                            expected_stage=next_node.node_id,
                        )
                except ValueError as exc:
                    return await self._finalize_run(
                        session,
                        run,
                        status_type=RunStatusType.FAILED,
                        outcome_type=RunOutcomeType.FAILED,
                        stop_reason=str(exc),
                        workflow_node=next_node.node_id,
                        dispatched=True,
                        notify_pending=notify_pending,
                        issue_ref=issue_ref,
                        org=context.org,
                        repo=context.repo,
                    )

                if next_node.node_id == LEARNING_EXTRACT_NODE:
                    try:
                        tip_raw = handoff.signals.get("tip_sha")
                        source_sha = str(tip_raw).strip() if tip_raw else None
                        prior_raw = payload.get("prior_run_id")
                        prior_run_id: Optional[UUID] = None
                        if prior_raw:
                            prior_run_id = UUID(str(prior_raw))
                        await self._learning_ingest_service.ingest_after_learning_extract(
                            session,
                            run,
                            workspace_path,
                            source_sha=source_sha,
                            prior_run_id=prior_run_id,
                        )
                    except (ValueError, TypeError) as exc:
                        return await self._finalize_run(
                            session,
                            run,
                            status_type=RunStatusType.FAILED,
                            outcome_type=RunOutcomeType.FAILED,
                            stop_reason=str(exc),
                            workflow_node=next_node.node_id,
                            dispatched=True,
                            notify_pending=notify_pending,
                            issue_ref=issue_ref,
                            org=context.org,
                            repo=context.repo,
                            handoff=handoff,
                        )

                if handoff.outcome == "findings":
                    retry_counter += 1
                    await self._run_repository.update_run(
                        session,
                        run_id,
                        RunUpdate(retry_counter=retry_counter),
                    )

                decision = self._policy_engine.evaluate_dispatch(
                    handoff,
                    context,
                    retry_counter=retry_counter,
                )

                if decision.decision == PolicyDecisionType.DISPATCH and decision.next_node:
                    if self._closure_forbids_node(payload, decision.next_node.node_id):
                        return await self._finalize_run(
                            session,
                            run,
                            status_type=RunStatusType.FAILED,
                            outcome_type=RunOutcomeType.FAILED,
                            stop_reason=(
                                f"Closure walk must not dispatch meta purge node "
                                f"{decision.next_node.node_id!r} (REQ-15)"
                            ),
                            workflow_node=decision.next_node.node_id,
                            dispatched=True,
                            notify_pending=notify_pending,
                            issue_ref=issue_ref,
                            org=context.org,
                            repo=context.repo,
                            handoff=handoff,
                            job_payload=payload,
                        )
                    next_node = decision.next_node
                    self.logger.info(
                        "Walker continuing to next orchestrated node",
                        run_id=str(run_id),
                        next_node=next_node.node_id,
                        hop_count=hop_count,
                    )
                    continue

                if decision.decision == PolicyDecisionType.APPLY_FORGE and decision.next_node:
                    apply_result = await self._apply_automated_forge(
                        session,
                        run=run,
                        next_node=decision.next_node,
                        handoff=handoff,
                        workspace_path=workspace_path,
                        payload=payload,
                    )
                    if apply_result.get("error"):
                        return await self._finalize_run(
                            session,
                            run,
                            status_type=RunStatusType.FAILED,
                            outcome_type=RunOutcomeType.FAILED,
                            stop_reason=str(apply_result["error"]),
                            workflow_node=decision.next_node.node_id,
                            dispatched=True,
                            notify_pending=notify_pending,
                            issue_ref=issue_ref,
                            org=context.org,
                            repo=context.repo,
                            handoff=handoff,
                            job_payload=payload,
                        )
                    if apply_result.get("pr_number") is not None:
                        refreshed = await self._run_repository.update_run(
                            session,
                            run_id,
                            RunUpdate(pr_number=int(apply_result["pr_number"])),
                        )
                        if refreshed is not None:
                            run = refreshed
                        issue_ref = run.pr_number or issue_ref
                    # Treat automated EA as passed; re-resolve without another skill hop.
                    handoff = HandoffEnvelope(
                        contract=handoff.contract,
                        stage=decision.next_node.node_id,
                        outcome="pass",
                        blockers=[],
                        human_checkpoint=False,
                        external_action=False,
                        forge=handoff.forge,
                    )
                    last_node_id = decision.next_node.node_id
                    self.logger.info(
                        "Automated forge applied; continuing walker",
                        run_id=str(run_id),
                        workflow_node=decision.next_node.node_id,
                        pr_number=apply_result.get("pr_number"),
                    )
                    decision = self._policy_engine.evaluate_dispatch(
                        handoff,
                        context,
                        retry_counter=retry_counter,
                    )
                    if decision.decision == PolicyDecisionType.DISPATCH and decision.next_node:
                        if self._closure_forbids_node(payload, decision.next_node.node_id):
                            return await self._finalize_run(
                                session,
                                run,
                                status_type=RunStatusType.FAILED,
                                outcome_type=RunOutcomeType.FAILED,
                                stop_reason=(
                                    f"Closure walk must not dispatch meta purge node "
                                    f"{decision.next_node.node_id!r} (REQ-15)"
                                ),
                                workflow_node=decision.next_node.node_id,
                                dispatched=True,
                                notify_pending=notify_pending,
                                issue_ref=issue_ref,
                                org=context.org,
                                repo=context.repo,
                                handoff=handoff,
                                job_payload=payload,
                            )
                        next_node = decision.next_node
                        self.logger.info(
                            "Walker continuing to next orchestrated node",
                            run_id=str(run_id),
                            next_node=next_node.node_id,
                            hop_count=hop_count,
                        )
                        continue
                    if decision.decision == PolicyDecisionType.BLOCK:
                        return await self._finalize_run(
                            session,
                            run,
                            status_type=RunStatusType.FAILED,
                            outcome_type=RunOutcomeType.BLOCKED,
                            stop_reason=decision.block_reason or "Policy BLOCK",
                            workflow_node=(
                                decision.next_node.node_id if decision.next_node else last_node_id
                            ),
                            dispatched=True,
                            notify_pending=notify_pending,
                            issue_ref=issue_ref,
                            org=context.org,
                            repo=context.repo,
                            handoff=handoff,
                        )
                    # Fall through to STOP handling (e.g. wave-acceptance)

                if decision.decision == PolicyDecisionType.BLOCK:
                    return await self._finalize_run(
                        session,
                        run,
                        status_type=RunStatusType.FAILED,
                        outcome_type=RunOutcomeType.BLOCKED,
                        stop_reason=decision.block_reason or "Policy BLOCK",
                        workflow_node=(
                            decision.next_node.node_id if decision.next_node else last_node_id
                        ),
                        dispatched=True,
                        notify_pending=notify_pending,
                        issue_ref=issue_ref,
                        org=context.org,
                        repo=context.repo,
                        handoff=handoff,
                    )

                # STOP at gate (checkpoint / manual / terminal / findings budget)
                stop_node = decision.next_node.node_id if decision.next_node else last_node_id
                stop_reason = decision.block_reason or f"Stopped at gate node {stop_node}"

                if (
                    decision.next_node is not None
                    and decision.next_node.node_type == "external-action"
                    and decision.next_node.forge.action is not None
                ):
                    try:
                        effective = merge_pin_and_handoff_forge(
                            decision.next_node.forge,
                            handoff.forge,
                        )
                    except ValueError as exc:
                        return await self._finalize_run(
                            session,
                            run,
                            status_type=RunStatusType.FAILED,
                            outcome_type=RunOutcomeType.FAILED,
                            stop_reason=str(exc),
                            workflow_node=stop_node,
                            dispatched=True,
                            notify_pending=notify_pending,
                            issue_ref=issue_ref,
                            org=context.org,
                            repo=context.repo,
                            handoff=handoff,
                        )
                    await self._run_event_repository.append_event(
                        session,
                        RunEventCreate(
                            run_id=run_id,
                            event_type="forge_pending",
                            workflow_node=stop_node,
                            payload={
                                "event_type": "forge_pending",
                                "action": effective.action.value,
                                "draft": effective.draft,
                                "apply_labels": effective.apply_labels,
                                "requires": decision.next_node.forge.requires,
                            },
                        ),
                    )
                    stop_reason = (
                        f"Pending forge authorization for {stop_node} "
                        f"action={effective.action.value} "
                        "(POST /api/v1/runs/{run_id}/forge/authorize)"
                    )

                return await self._finalize_run(
                    session,
                    run,
                    status_type=RunStatusType.STOPPED,
                    outcome_type=RunOutcomeType.STOPPED,
                    stop_reason=stop_reason,
                    workflow_node=stop_node,
                    dispatched=True,
                    notify_pending=notify_pending,
                    issue_ref=issue_ref,
                    org=context.org,
                    repo=context.repo,
                    handoff=handoff,
                    stop_node=decision.next_node,
                    job_payload=payload,
                )

    async def _run_orchestrated_stage(
        self,
        session: AsyncSession,
        *,
        run: RunModel,
        run_id: UUID,
        context_org: str,
        context_repo: str,
        issue_ref: Optional[int],
        next_node: ResolvedWorkflowNode,
        resolved: ResolvedNodeDispatch,
        workspace_path: str,
        payload: dict[str, Any],
        initiative_id: Optional[str],
    ) -> dict[str, Any]:
        """Execute one Cursor stage; return success flag and notify_pending."""
        started_at = datetime.now(UTC)
        await self._run_event_repository.append_event(
            session,
            RunEventCreate(
                run_id=run_id,
                event_type="stage_started",
                workflow_node=next_node.node_id,
                payload={
                    "event_type": "stage_started",
                    "runner": resolved.runner,
                    "model_id": resolved.model_id,
                    "model_profile": resolved.model_profile,
                },
            ),
        )
        # W3: stage_started is timeline-only; Notifier skips PR mirror.
        notify_pending = await self._post_run_event(
            context_org,
            context_repo,
            issue_ref,
            run_id,
            next_node.node_id,
            RunEventNameType.STAGE_STARTED,
            outcome=None,
            duration_ms=None,
            timestamp=started_at,
        )

        prompt_context: dict[str, Any] = {
            "initiative_id": initiative_id or payload.get("initiative_id"),
            "start_node": next_node.node_id,
            "workflow_node": next_node.node_id,
        }
        if isinstance(payload.get("prompt_context"), dict):
            prompt_context.update(payload["prompt_context"])

        try:
            handoff_path = await self._ensure_run_handoff_path(session, run=run, run_id=run_id)
            ticket = self._require_ticket_from_payload(payload)
            initiative = str(initiative_id or payload.get("initiative_id") or "")
            package = self._prompt_resolver.resolve_package(workspace_path, next_node.node_id)
            meta_workspace = payload.get("meta_workspace_path")
            meta_pr_url = payload.get("meta_pr_url")
            rendered = self._prompt_resolver.bind_and_render(
                package,
                BoundPromptInputs(
                    ticket=ticket,
                    initiative=initiative,
                    skill_id=next_node.node_id,
                    workspace=workspace_path,
                    handoff_path=handoff_path,
                    meta_workspace=(
                        str(meta_workspace).strip()
                        if meta_workspace is not None and str(meta_workspace).strip()
                        else None
                    ),
                    meta_pr_url=(
                        str(meta_pr_url).strip()
                        if meta_pr_url is not None and str(meta_pr_url).strip()
                        else None
                    ),
                ),
            )
        except (PromptResolveError, ValueError) as exc:
            duration_ms = 0
            ended_at = datetime.now(UTC)
            reason = str(exc)
            await self._metrics_emitter.record_stage_duration(
                session,
                run_id,
                next_node.node_id,
                duration_ms,
                outcome="failed",
                runner=resolved.runner,
                model_id=resolved.model_id,
                model_profile=resolved.model_profile,
                lane=self._optional_lane_from_job_payload(payload),
            )
            await self._stage_repository.create_stage(
                session,
                StageCreate(
                    run_id=run_id,
                    workflow_node=next_node.node_id,
                    outcome_type=RunOutcomeType.FAILED,
                    started_at=started_at,
                    ended_at=ended_at,
                    runner=resolved.runner,
                    model_profile=resolved.model_profile,
                    model_id=resolved.model_id,
                    model_provider=resolved.model_provider,
                ),
            )
            completed_notify = await self._post_run_event(
                context_org,
                context_repo,
                issue_ref,
                run_id,
                next_node.node_id,
                RunEventNameType.STAGE_COMPLETED,
                outcome=RunOutcomeType.FAILED.value,
                duration_ms=duration_ms,
                timestamp=ended_at,
            )
            return {
                "success": False,
                "notify_pending": notify_pending or completed_notify,
                "stop_reason": reason,
                "duration_ms": duration_ms,
            }

        catalogue_credential: Optional[str] = None
        if resolved.runner == "cursor":
            catalogue_credential = await self._catalogue_repository.get_credential(
                session, "cursor"
            )
        t0 = time.monotonic()
        agent_result = await self._cursor_agent_runner.run_skill(
            workspace_path=workspace_path,
            skill_id=next_node.node_id,
            prompt_context=prompt_context,
            model_profile=resolved.model_profile,
            message=rendered.message,
            runner=resolved.runner,
            model_id=resolved.model_id,
            model_provider=resolved.model_provider,
            credential=catalogue_credential,
        )
        duration_ms = int((time.monotonic() - t0) * 1000)

        # Agent binary success/failure gates walker continuation; skill verdict
        # (handoff.outcome) drives persisted stage/event outcome vocabulary (REQ-01).
        agent_ok = agent_result.outcome == AgentRunOutcomeType.SUCCESS
        handoff_for_outcome: Optional[HandoffEnvelope] = None
        if not agent_ok:
            stage_outcome = RunOutcomeType.FAILED
        else:
            try:
                handoff_for_outcome = self._ingest_handoff_after_stage(
                    handoff_path=handoff_path,
                    expected_stage=next_node.node_id,
                )
                stage_outcome = self._stage_outcome_from_handoff_outcome(
                    handoff_for_outcome.outcome
                )
            except ValueError:
                # Handoff not readable yet — persist agent SUCCESS; caller
                # re-ingests and remains the fail-closed gate (REQ-8b).
                stage_outcome = RunOutcomeType.SUCCESS
                handoff_for_outcome = None
        metrics_outcome = stage_outcome.value
        ended_at = datetime.now(UTC)
        await self._metrics_emitter.record_stage_duration(
            session,
            run_id,
            next_node.node_id,
            duration_ms,
            outcome=metrics_outcome,
            runner=resolved.runner,
            model_id=resolved.model_id,
            model_profile=resolved.model_profile,
            lane=self._optional_lane_from_job_payload(payload),
        )
        await self._stage_repository.create_stage(
            session,
            StageCreate(
                run_id=run_id,
                workflow_node=next_node.node_id,
                outcome_type=stage_outcome,
                started_at=started_at,
                ended_at=ended_at,
                runner=resolved.runner,
                model_profile=resolved.model_profile,
                model_id=resolved.model_id,
                model_provider=resolved.model_provider,
                prompt_id=rendered.prompt_id,
                prompt_revision=rendered.prompt_revision,
            ),
        )
        completed_notify = await self._post_run_event(
            context_org,
            context_repo,
            issue_ref,
            run_id,
            next_node.node_id,
            RunEventNameType.STAGE_COMPLETED,
            outcome=stage_outcome.value,
            duration_ms=duration_ms,
            timestamp=ended_at,
        )
        notify_pending = notify_pending or completed_notify
        return {
            "success": agent_ok,
            "notify_pending": notify_pending,
            "stop_reason": agent_result.error_message,
            "duration_ms": duration_ms,
            "handoff_path": handoff_path,
            "handoff": handoff_for_outcome,
        }

    async def _resolve_job_workspace_path(
        self,
        *,
        org: str,
        repo: str,
        workspace_path: Optional[str],
    ) -> tuple[str, bool]:
        """Explicit path wins (REQ-12); omitted path uses tenant clone/fetch (REQ-10/15).

        Returns ``(absolute_path, tenant_bound)``. ``tenant_bound`` is True only for
        the omitted-path clone/fetch path so REQ-19 checkout never mutates an
        explicit caller workspace (including unit-test ``Path.cwd()``).
        """
        if workspace_path is not None and str(workspace_path).strip():
            return str(workspace_path).strip(), False

        credential = await self._tenant_service.get_workspace_credential_for_repo(
            org=org,
            repo=repo,
        )
        if credential is None:
            raise ValueError(
                "workspace_path omitted and org/repo is not Tenant-registered; "
                "refusing Path.cwd() fallback"
            )
        resolved = await self._tenant_git_workspace_client.resolve_workspace(credential)
        return resolved.path, True

    async def _require_tenant_id_for_repo(self, *, org: str, repo: str) -> UUID:
        credential = await self._tenant_service.get_workspace_credential_for_repo(
            org=org, repo=repo
        )
        if credential is None:
            raise UnprocessableEntityError(
                message="No tenant registration for org/repo — cannot attribute run",
                details={"org": org, "repo": repo, "reason": "tenant_not_registered"},
            )
        return credential.tenant_id

    async def _ensure_harness_ready(
        self,
        *,
        org: str,
        repo: str,
        workspace_path: str,
        force: bool = False,
    ) -> None:
        """Probe harness after workspace resolve; honor verified cache (REQ-20–22).

        Provenance switch (ADR-013): ``launchpad_status`` → status client;
        NULL/filesystem → ``sync_harness``. Legacy force-recheck never calls status.
        """
        registered = await self._tenant_service.get_workspace_credential_for_repo(
            org=org,
            repo=repo,
        )
        readiness_source = (
            await self._tenant_service.get_readiness_source(org=org, repo=repo)
            if registered is not None
            else None
        )
        use_status = readiness_source == ReadinessSourceType.LAUNCHPAD_STATUS
        evaluator = "launchpad_status" if use_status else "filesystem"

        if registered is not None and not force:
            if await self._tenant_service.is_harness_verified(org=org, repo=repo):
                self.logger.info(
                    "Harness readiness skipped (cached verified)",
                    org=org,
                    repo=repo,
                    workspace_path=workspace_path,
                    evaluator=evaluator,
                    cache_hit=True,
                )
                return

        if use_status:
            assert registered is not None
            if not force:
                raise UnprocessableEntityError(
                    message="Selected repo has not passed Launchpad status readiness",
                    details={
                        "org": org,
                        "repo": repo,
                        "reason": "never_checked",
                        "evaluator": evaluator,
                    },
                )
            connection = await self._tenant_service.get_programme_connection(registered.tenant_id)
            if connection is None:
                raise UnprocessableEntityError(
                    message="Tenant has no programme connection for status readiness",
                    details={"org": org, "repo": repo, "reason": "programme_not_connected"},
                )
            meta_config_dir = str(
                Path(registered.workspace_root) / connection.org / connection.repo
            )
            try:
                verdict = await self._launchpad_status_client.inspect_status(
                    repo_workspace=workspace_path,
                    meta_config_dir=meta_config_dir,
                    org=org,
                    repo=repo,
                    pat=registered.pat,
                )
            except LaunchpadStatusError as exc:
                raise UnprocessableEntityError(
                    message=str(exc),
                    details={"org": org, "repo": repo, "reason": exc.reason},
                ) from exc
            if not verdict.ready:
                await self._tenant_service.mark_harness_verified(org=org, repo=repo, verified=False)
                raise UnprocessableEntityError(
                    message="Launchpad status reported repo not ready",
                    details={
                        "org": org,
                        "repo": repo,
                        "reason": verdict.reason or "repo_not_ready",
                        "evaluator": evaluator,
                    },
                )
            await self._tenant_service.mark_harness_verified(org=org, repo=repo, verified=True)
            return

        await self._launchpad_client.sync_harness(workspace_path)
        if registered is not None:
            await self._tenant_service.mark_harness_verified(org=org, repo=repo, verified=True)

    async def _ensure_run_handoff_path(
        self,
        session: AsyncSession,
        *,
        run: RunModel,
        run_id: UUID,
    ) -> str:
        """Return stored handoff_path; define under GATEFLOW_HANDOFF_ROOT when missing."""
        if run.handoff_path and str(run.handoff_path).strip():
            return str(run.handoff_path).strip()
        root = self._orchestration.require_handoff_root()
        baton_dir = Path(root) / str(run_id)
        baton_dir.mkdir(parents=True, exist_ok=True)
        baton_path = baton_dir / "handoff.md"
        if not baton_path.exists():
            baton_path.write_text("", encoding="utf-8")
        handoff_path = str(baton_path.resolve())
        await self._run_repository.update_run(
            session,
            run_id,
            RunUpdate(handoff_path=handoff_path),
        )
        return handoff_path

    def _require_ticket_from_payload(self, payload: dict[str, Any]) -> str:
        ticket = payload.get("ticket_id")
        if ticket is None or not str(ticket).strip():
            raise ValueError("ticket_id missing from job payload for packaged-skill automate")
        return str(ticket).strip()

    def _optional_lane_from_job_payload(
        self, job_payload: Optional[dict[str, Any]]
    ) -> Optional[str]:
        """Return non-empty lane from job payload, or None (never fabricate)."""
        if job_payload is None:
            return None
        raw = job_payload.get("lane")
        if isinstance(raw, str) and raw.strip():
            return raw.strip()
        return None

    def _stage_outcome_from_handoff_outcome(self, outcome: str) -> RunOutcomeType:
        """Map skill handoff.outcome onto RunOutcomeType (REQ-01).

        Workflow ``pass`` is the success synonym; other values must match the
        persisted enum wire strings.
        """
        normalized = outcome.strip()
        if normalized == "pass":
            return RunOutcomeType.SUCCESS
        try:
            return RunOutcomeType(normalized)
        except ValueError as exc:
            raise ValueError(
                f"Unrecognized handoff.outcome {outcome!r} for stage persistence"
            ) from exc

    def _ingest_handoff_after_stage(
        self,
        *,
        handoff_path: str,
        expected_stage: str,
    ) -> HandoffEnvelope:
        """Ingest durable handoff from stored run.handoff_path only (ADR-008 / REQ-8b).

        Ambient glob/mtime discovery is not automate SSOT. Missing or unreadable
        path fails closed via HandoffReader.read_path.
        """
        if not handoff_path or not str(handoff_path).strip():
            raise ValueError("run.handoff_path is required for packaged-skill automate ingest")
        handoff = self._handoff_reader.read_path(str(handoff_path).strip())
        if handoff.stage != expected_stage:
            raise ValueError(
                f"Handoff stage {handoff.stage!r} does not match executed node "
                f"{expected_stage!r}"
            )
        return handoff

    async def _publish_stage_workspace_if_needed(
        self,
        session: AsyncSession,
        *,
        run: RunModel,
        workspace_path: str,
        node_id: str,
        payload: dict[str, Any],
    ) -> None:
        """Apply pin ``forge.commit_workspace`` after a successful skill hop (before ingest).

        Head ref is bound from run/wave PR targeting — never from handoff.forge.head.
        """
        if run.id is None:
            raise RuntimeError("Run missing id before stage commit")

        executed = self._workflow_engine.get_node(node_id)
        mode = executed.forge.commit_workspace
        if mode == CommitWorkspaceModeType.DISABLED:
            return

        handoff_root: Optional[str] = None
        if self._orchestration.has_handoff_root():
            handoff_root = self._orchestration.require_handoff_root()

        head = self._require_run_head_branch(run=run, payload=payload)
        try:
            async with self._forge_client_factory.session_for_repo(run.org, run.repo) as forge:
                remote_tip = await forge.get_branch_tip_sha(run.org, run.repo, branch=head)
        except Exception as tip_exc:
            self.logger.error(
                "Failed to resolve run head tip for stage publish",
                run_id=str(run.id),
                workflow_node=node_id,
                head=head,
                error=str(tip_exc),
                exc_info=True,
            )
            raise ValueError(
                f"forge.commit_workspace could not resolve tip for branch {head!r}: " f"{tip_exc}"
            ) from tip_exc

        # Skills leave dirty trees; Forge publishes. base_ref covers mistaken
        # local commits ahead of the remote run head (safety net).
        paths = collect_commit_paths(
            workspace_path,
            handoff_root=handoff_root,
            base_ref=remote_tip,
        )
        if not paths:
            if mode == CommitWorkspaceModeType.REQUIRED:
                raise ValueError(
                    f"forge.commit_workspace=required for node {node_id!r} but "
                    "no includable workspace paths to publish "
                    f"(dirty empty and no files ahead of remote tip {remote_tip[:12]})"
                )
            self.logger.info(
                "Stage commit skipped — no includable paths",
                run_id=str(run.id),
                workflow_node=node_id,
                commit_workspace=mode.value,
                remote_tip=remote_tip,
            )
            return

        message = f"chore(gateflow): stage {node_id} workspace publish"
        try:
            async with self._forge_client_factory.session_for_repo(run.org, run.repo) as forge:
                result = await forge.commit_paths_to_branch(
                    run.org,
                    run.repo,
                    branch=head,
                    workspace_path=workspace_path,
                    paths=paths,
                    message=message,
                )
        except Exception as exc:
            self.logger.error(
                "Stage forge commit failed",
                run_id=str(run.id),
                workflow_node=node_id,
                head=head,
                path_count=len(paths),
                error=str(exc),
                exc_info=True,
            )
            raise ValueError(f"forge.commit_workspace failed for node {node_id!r}: {exc}") from exc

        await self._run_event_repository.append_event(
            session,
            RunEventCreate(
                run_id=run.id,
                event_type="stage_commit",
                workflow_node=node_id,
                payload={
                    "event_type": "stage_commit",
                    "commit_sha": result.commit_sha,
                    "branch": result.branch,
                    "path_count": result.path_count,
                    "paths": result.paths,
                    "commit_workspace": mode.value,
                },
            ),
        )
        self.logger.info(
            "Stage workspace committed to run head",
            run_id=str(run.id),
            workflow_node=node_id,
            commit_sha=result.commit_sha,
            branch=result.branch,
            path_count=result.path_count,
            commit_workspace=mode.value,
        )

    def _require_run_head_branch(self, *, run: RunModel, payload: dict[str, Any]) -> str:
        """Bind publish head from job payload (pin forbids forge.head).

        Closeout Pass-2 sets ``head_ref`` from the open wave PR. Spec lane sets
        ``head_ref`` to ``feature/{INIT}-spec``. When present, that ref is SSOT —
        do not invent a head from ``branch_slug``. Spec lane without ``head_ref``
        still uses ``build_spec_head_branch`` (ignores wave_id / branch_slug).
        """
        raw_head = payload.get("head_ref")
        if isinstance(raw_head, str) and raw_head.strip():
            return raw_head.strip()

        initiative_id = run.initiative_id or payload.get("initiative_id")
        lane = str(payload.get("lane") or "").strip()
        if lane == "spec":
            if not initiative_id:
                raise ValueError(
                    "Stage forge commit requires initiative_id on the run/job "
                    "payload for spec-lane head (or head_ref)"
                )
            return build_spec_head_branch(str(initiative_id))
        if lane == "closure":
            if not initiative_id:
                raise ValueError(
                    "Stage forge commit requires initiative_id on the run/job "
                    "payload for closure-lane head (or head_ref)"
                )
            branch_slug = payload.get("branch_slug")
            if not branch_slug:
                raise ValueError(
                    "closure-lane head requires branch_slug on the job payload (or head_ref)"
                )
            return build_closure_head_branch(str(initiative_id), str(branch_slug))

        wave_id = run.wave_id or payload.get("wave_id")
        branch_slug = payload.get("branch_slug")
        if not initiative_id or not wave_id or not branch_slug:
            raise ValueError(
                "Stage forge commit requires initiative_id, wave_id, and branch_slug "
                "on the run/job payload to bind the run head branch "
                "(or head_ref when closeout-bound to a wave PR)"
            )
        return build_wave_head_branch(
            str(initiative_id),
            str(wave_id),
            str(branch_slug),
        )

    async def resolve_branch(
        self,
        *,
        org: str,
        repo: str,
        run: RunModel,
        payload: dict[str, Any],
    ) -> tuple[str, BranchResolveModeType]:
        """Compose new-wave fork vs continuation reuse (TDD §3.5 / REQ-16–18).

        - Explicit ``head_ref`` (closeout / PR-bound): verify remote tip; never create.
        - Otherwise: if the deterministic head already exists on remote → continuation
          (zero ``ensure_branch_from_base``); else fork from live ``base_branch`` tip.
        """
        base_branch = payload.get("base_branch")
        if not base_branch:
            raise ValueError(
                "ensure_branch requires base_branch on the wave-start job payload "
                "(caller-owned targeting)"
            )

        try:
            head = self._require_run_head_branch(run=run, payload=payload)
            base = validate_base_branch(str(base_branch))
        except ValueError as exc:
            raise ValueError(f"Invalid branch targeting for run start: {exc}") from exc

        raw_head = payload.get("head_ref")
        explicit_continuation = bool(raw_head is not None and str(raw_head).strip())

        if explicit_continuation:
            initiative_id = payload.get("initiative_id") or run.initiative_id
            wave_id = payload.get("wave_id") or run.wave_id
            derived_slug: Optional[str] = None
            if initiative_id and wave_id:
                derived_slug = branch_slug_from_head_ref(
                    head,
                    initiative_id=str(initiative_id),
                    wave_id=str(wave_id),
                )
            try:
                async with self._forge_client_factory.session_for_repo(org, repo) as forge:
                    await forge.get_branch_tip_sha(org, repo, branch=head)
            except Exception as exc:
                raise ValueError("continuation branch not found on remote") from exc
            self.logger.info(
                "Resolved continuation head (explicit head_ref)",
                org=org,
                repo=repo,
                head=head,
                base=base,
                mode=BranchResolveModeType.CONTINUATION.value,
                branch_slug=derived_slug,
            )
            return head, BranchResolveModeType.CONTINUATION

        if await self._remote_branch_exists(org, repo, head):
            self.logger.info(
                "Resolved continuation head (remote exists)",
                org=org,
                repo=repo,
                head=head,
                base=base,
                mode=BranchResolveModeType.CONTINUATION.value,
            )
            return head, BranchResolveModeType.CONTINUATION

        async with self._forge_client_factory.session_for_repo(org, repo) as forge:
            await forge.ensure_branch_from_base(
                org,
                repo,
                branch=head,
                base=base,
            )
        self.logger.info(
            "Resolved new-wave head from live base tip",
            org=org,
            repo=repo,
            head=head,
            base=base,
            mode=BranchResolveModeType.NEW_WAVE.value,
        )
        return head, BranchResolveModeType.NEW_WAVE

    async def _remote_branch_exists(self, org: str, repo: str, branch: str) -> bool:
        try:
            async with self._forge_client_factory.session_for_repo(org, repo) as forge:
                tip = await forge.get_branch_tip_sha(org, repo, branch=branch)
        except Exception:
            return False
        return bool(str(tip).strip())

    async def _ensure_run_branch(
        self,
        session: AsyncSession,
        run: RunModel,
        *,
        payload: dict[str, Any],
        notify_pending: bool,
    ) -> tuple[RunModel, bool, Optional[str]]:
        """Resolve wave head (new vs continuation); do not open a Draft PR at start."""
        if run.id is None:
            raise RuntimeError("Run missing id before ensure_branch")

        try:
            head, mode = await self.resolve_branch(
                org=run.org,
                repo=run.repo,
                run=run,
                payload=payload,
            )
        except ValueError:
            raise
        except Exception as exc:
            self.logger.error(
                "resolve_branch failed at run start",
                run_id=str(run.id),
                error=str(exc),
                exc_info=True,
            )
            updated = await self._run_repository.update_run(
                session,
                run.id,
                RunUpdate(notify_pending=True),
            )
            return (updated or run), True, None

        self.logger.info(
            "Run head branch resolved at start (no PR create)",
            run_id=str(run.id),
            head=head,
            mode=mode.value,
            pr_number=run.pr_number,
        )
        return run, notify_pending, head

    async def _apply_automated_forge(
        self,
        session: AsyncSession,
        *,
        run: RunModel,
        next_node: ResolvedWorkflowNode,
        handoff: HandoffEnvelope,
        workspace_path: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Apply automated external-action forge; return pr_number or error."""
        if run.id is None:
            return {"error": "Run missing id for automated forge apply"}
        workspace = Path(workspace_path).resolve()
        if not workspace.is_dir():
            return {"error": f"workspace_path is not a directory: {workspace}"}

        try:
            head = self._require_run_head_branch(run=run, payload=payload)
            base_raw = payload.get("base_branch")
            if not base_raw:
                return {"error": "base_branch required on job payload for automated open_draft_pr"}
            base = validate_base_branch(str(base_raw))
        except ValueError as exc:
            return {"error": str(exc)}

        try:
            applied = await self._forge_action_service.apply_external_action(
                org=run.org,
                repo=run.repo,
                node=next_node,
                handoff=handoff,
                workspace=workspace,
                head_ref=head,
                base_ref=base,
                ticket_ref=str(payload.get("ticket_id") or "").strip() or None,
            )
        except ValidationError as exc:
            return {"error": exc.message}
        except Exception as exc:
            self.logger.error(
                "Automated forge apply failed",
                run_id=str(run.id),
                workflow_node=next_node.node_id,
                error=str(exc),
                exc_info=True,
            )
            return {"error": str(exc)}

        await self._run_event_repository.append_event(
            session,
            RunEventCreate(
                run_id=run.id,
                event_type="forge_executed",
                workflow_node=next_node.node_id,
                payload={
                    "event_type": "forge_executed",
                    "action": applied.action.value,
                    "pr_number": applied.pr_number,
                    "authorization": "automated",
                },
            ),
        )
        return {"pr_number": applied.pr_number}

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

    @staticmethod
    def _compute_wave_duration_ms(run: RunModel, ended_at: datetime) -> Optional[int]:
        if run.created_at is None:
            return None
        started = run.created_at
        if started.tzinfo is None:
            started = started.replace(tzinfo=UTC)
        end = ended_at if ended_at.tzinfo is not None else ended_at.replace(tzinfo=UTC)
        return max(0, int((end - started).total_seconds() * 1000))

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
        handoff: Optional[HandoffEnvelope] = None,
        stop_node: Optional[ResolvedWorkflowNode] = None,
        job_payload: Optional[dict[str, Any]] = None,
    ) -> RunProcessSummary:
        if run.id is None:
            raise RuntimeError("Run missing id during finalize")

        ended_at = datetime.now(UTC)
        wave_duration_ms = self._compute_wave_duration_ms(run, ended_at)

        payload: dict[str, Any] = {
            "stop_reason": stop_reason,
            "event_type": "run_stopped",
            "wave_duration_ms": wave_duration_ms,
        }
        lane = self._optional_lane_from_job_payload(job_payload)
        if lane is not None:
            payload["lane"] = lane
        if stop_node is not None:
            if stop_node.purpose is not None:
                payload["purpose"] = stop_node.purpose
            if stop_node.owner is not None:
                payload["owner"] = stop_node.owner
        if handoff is not None:
            payload["handoff_context"] = {
                "stage": handoff.stage,
                "outcome": handoff.outcome,
                "blockers": list(handoff.blockers),
                "signals": dict(handoff.signals),
                "next_candidates": list(handoff.next_candidates),
                "human_checkpoint": handoff.human_checkpoint,
            }
        partial = self._partial_closure_failure_payload(
            job_payload=job_payload,
            status_type=status_type,
        )
        if partial:
            payload.update(partial)
            self.logger.warning(
                "Partial closure failure after EPIC Done (REQ-20)",
                run_id=str(run.id),
                workflow_node=workflow_node,
                stop_reason=stop_reason,
            )

        await self._run_event_repository.append_event(
            session,
            RunEventCreate(
                run_id=run.id,
                event_type="run_stopped",
                workflow_node=workflow_node,
                outcome_type=outcome_type,
                payload=payload,
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
                duration_ms=wave_duration_ms,
                timestamp=ended_at,
            )
            notify_pending = notify_pending or stopped_notify

        await self._run_repository.update_run(
            session,
            run.id,
            RunUpdate(
                status_type=status_type,
                outcome_type=outcome_type,
                workflow_node=workflow_node,
                wave_duration_ms=wave_duration_ms,
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
            wave_duration_ms=wave_duration_ms,
        )
        return RunProcessSummary(
            run_id=run.id,
            terminal_status=status_type.value,
            stop_reason=stop_reason,
            dispatched=dispatched,
        )

    @staticmethod
    def _closure_forbids_node(payload: dict[str, Any], node_id: str) -> bool:
        """True when closure lane must not dispatch PM/meta purge nodes (REQ-15)."""
        if str(payload.get("lane") or "").strip() != "closure":
            return False
        return node_id in _CLOSURE_META_FORBIDDEN_NODES

    @staticmethod
    def _partial_closure_failure_payload(
        *,
        job_payload: Optional[dict[str, Any]],
        status_type: RunStatusType,
    ) -> dict[str, Any]:
        """REQ-20 — record partial failure after EPIC Done; no closure-complete claim."""
        if job_payload is None or status_type != RunStatusType.FAILED:
            return {}
        if not job_payload.get("epic_done_applied"):
            return {}
        if str(job_payload.get("lane") or "").strip() != "closure":
            return {}
        return {
            "partial_closure_failure": True,
            "closure_complete_claim": False,
            "epic_done_applied": True,
        }


def get_run_orchestrator() -> RunOrchestrator:
    from src.di.dependency_container import provide_service

    return provide_service(RunOrchestrator)
