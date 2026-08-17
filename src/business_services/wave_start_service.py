"""WaveStartService — authenticated lane starts (ADR-010 / INIT-006 W3+W4)."""

from pathlib import Path
from typing import Optional
from uuid import UUID, uuid4

import httpx
from injector import inject
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.exc import SQLAlchemyError

from src.business_services.base_business_service import BaseBusinessService
from src.business_services.board_service import BoardService
from src.business_services.checkpoint_evidence_service import CheckpointEvidenceService
from src.business_services.implement_ticket_gate import (
    assert_dual_identity_agreement,
    assert_implement_ticket_id_well_formed,
    assert_ticket_not_done,
    assert_ticket_resolvable,
    resolve_board_ticket_id,
)
from src.business_services.meta_pr_intake import MetaPrIntakeService
from src.business_services.metrics_emitter import MetricsEmitter
from src.business_services.slot_validator import SlotValidator
from src.business_services.tenant_service import TenantService
from src.business_services.trigger_router import API_TRIGGER_EVENT
from src.business_services.workflow_engine import WorkflowEngine
from src.configs.orchestration_settings import OrchestrationSettings
from src.database.postgres.repository.programme_meta_pr_repository import (
    ProgrammeMetaPrRepository,
)
from src.database.postgres.repository.programme_repository import ProgrammeRepository
from src.database.postgres.repository.run_store_repository import JobRepository, RunRepository
from src.exceptions.app_exceptions import (
    ConflictError,
    ServiceUnavailableError,
    UnprocessableEntityError,
    ValidationError,
)
from src.infra_services.forge_client import ForgeClient, ForgeClientFactory
from src.infra_services.launchpad_client import HarnessReadinessError, LaunchpadClient
from src.infra_services.launchpad_status_client import (
    LaunchpadStatusClient,
    LaunchpadStatusError,
)
from src.infra_services.postgres_service import PostgresService
from src.infra_services.tenant_git_workspace_client import (
    TenantGitWorkspaceClient,
    TenantGitWorkspaceError,
)
from src.models.board_models import BoardTicketStatusUpdateRequest
from src.models.checkpoint_models import (
    PRD_IMPACT_ACCEPTANCE_CHECKPOINT_ID,
    CheckpointPrRef,
    CheckpointVerdictType,
)
from src.models.lane_types import LaneType
from src.models.meta_pr_models import MetaPrAcceptResult
from src.models.programme_models import LaneRunnerDefault, ProgrammeReadModel
from src.models.tenant_git_workspace_models import TenantWorkspaceCredential
from src.models.pr_branch_naming import branch_slug_from_head_ref
from src.models.policy_types import WavePreconditionIdType
from src.models.programme_readiness_models import ReadinessSourceType
from src.models.run_store_models import JobCreate, RunCreate, RunUpdate
from src.models.run_store_types import JobStatusType, RunStatusType
from src.models.wave_start_models import (
    CLOSEOUT_START_NODE,
    SPEC_DEFAULT_BRANCH_SLUG,
    SPEC_DEFAULT_START_NODE,
    SPEC_DEFAULT_WAVE_ID,
    CloseoutWaveStartRequest,
    ImplementWaveStartRequest,
    SpecWaveStartRequest,
    WaveStartJobPayload,
    WaveStartResponse,
    WaveStartTargetingFields,
)


class WaveStartService(BaseBusinessService):
    """Accept programme-token lane starts: validate, persist run, enqueue job."""

    @inject
    def __init__(
        self,
        postgres_service: PostgresService,
        slot_validator: SlotValidator,
        workflow_engine: WorkflowEngine,
        metrics_emitter: MetricsEmitter,
        run_repository: RunRepository,
        job_repository: JobRepository,
        meta_pr_intake: MetaPrIntakeService,
        forge_client_factory: ForgeClientFactory,
        board_service: BoardService,
        tenant_service: TenantService,
        tenant_git_workspace_client: TenantGitWorkspaceClient,
        launchpad_client: LaunchpadClient,
        launchpad_status_client: LaunchpadStatusClient,
        programme_repository: ProgrammeRepository,
        programme_meta_pr_repository: ProgrammeMetaPrRepository,
        checkpoint_evidence_service: CheckpointEvidenceService,
    ) -> None:
        super().__init__()
        self._postgres_service = postgres_service
        self._slot_validator = slot_validator
        self._workflow_engine = workflow_engine
        self._metrics_emitter = metrics_emitter
        self._run_repository = run_repository
        self._job_repository = job_repository
        self._meta_pr_intake = meta_pr_intake
        self._forge_client_factory = forge_client_factory
        self._board_service = board_service
        self._tenant_service = tenant_service
        self._tenant_git_workspace_client = tenant_git_workspace_client
        self._launchpad_client = launchpad_client
        self._launchpad_status_client = launchpad_status_client
        self._programme_repository = programme_repository
        self._programme_meta_pr_repository = programme_meta_pr_repository
        self._checkpoint_evidence = checkpoint_evidence_service
        self._orchestration = OrchestrationSettings.get_instance()

    async def start_implement_wave(self, request: ImplementWaveStartRequest) -> WaveStartResponse:
        """Implement-lane start: ticket identity + Enter-at; no meta fields."""
        ticket = assert_implement_ticket_id_well_formed(ticket_id=request.ticket_id)
        assert_dual_identity_agreement(
            ticket_id=ticket,
            initiative_id=request.initiative_id,
            wave_id=request.wave_id,
        )
        assert_ticket_resolvable(ticket_id=ticket, issue_number=request.issue_number)
        board_ticket_id = resolve_board_ticket_id(
            ticket_id=ticket,
            issue_number=request.issue_number,
        )
        existing = await self._board_service.get_ticket(
            board_ticket_id,
            org=request.org,
            repo=request.repo,
        )
        assert_ticket_not_done(column=existing.column)
        initiative_id, wave_id, issue_number, ticket = self._resolve_ticket_identity(
            ticket_id=ticket,
            initiative_id=request.initiative_id,
            wave_id=request.wave_id,
            issue_number=request.issue_number,
        )
        workspace_path = await self._resolve_implement_workspace_path(request)
        if workspace_path is not None:
            await self._ensure_implement_harness_ready(
                org=request.org,
                repo=request.repo,
                workspace_path=workspace_path,
                force=request.force_harness_recheck,
            )
        await self._apply_implement_in_progress(
            org=request.org,
            repo=request.repo,
            ticket=ticket,
            issue_number=issue_number,
        )
        return await self._enqueue_wave(
            request,
            initiative_id=initiative_id,
            wave_id=wave_id,
            issue_number=issue_number,
            ticket=ticket,
            workspace_path=workspace_path,
            meta_accept=None,
            meta_workspace_path=None,
            prior_run_id=None,
            lane="implement",
        )

    async def _ensure_implement_harness_ready(
        self,
        *,
        org: str,
        repo: str,
        workspace_path: str,
        force: bool = False,
    ) -> None:
        """Harness probe before board/enqueue (REQ-20/21 → 422; 0 enqueue)."""
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
                    "Harness readiness skipped at wave-start (cached verified)",
                    org=org,
                    repo=repo,
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
            self.logger.info(
                "Harness readiness ok at wave-start",
                org=org,
                repo=repo,
                evaluator=evaluator,
                cache_hit=False,
            )
            return

        # Filesystem evaluator (legacy / NULL readiness_source) — including force-recheck.
        try:
            await self._launchpad_client.sync_harness(workspace_path)
        except FileNotFoundError as exc:
            raise UnprocessableEntityError(
                message=str(exc),
                details={"org": org, "repo": repo, "reason": "workspace_path_missing"},
            ) from exc
        except HarnessReadinessError as exc:
            raise UnprocessableEntityError(
                message=str(exc),
                details={
                    "org": org,
                    "repo": repo,
                    "reason": exc.reason,
                    "missing": exc.missing,
                },
            ) from exc
        if registered is not None:
            await self._tenant_service.mark_harness_verified(org=org, repo=repo, verified=True)
        self.logger.info(
            "Harness readiness ok at wave-start",
            org=org,
            repo=repo,
            evaluator=evaluator,
            cache_hit=False,
        )

    async def _resolve_implement_workspace_path(
        self, request: ImplementWaveStartRequest
    ) -> Optional[str]:
        """Honor explicit path (REQ-12); resolve or 422 when omitted (REQ-10/15)."""
        if request.workspace_path is not None and str(request.workspace_path).strip():
            return str(request.workspace_path).strip()

        credential = await self._tenant_service.get_workspace_credential_for_repo(
            org=request.org,
            repo=request.repo,
        )
        if credential is None:
            raise UnprocessableEntityError(
                message=(
                    "workspace_path omitted and org/repo is not Tenant-registered; "
                    "refusing to guess a workspace"
                ),
                details={
                    "org": request.org,
                    "repo": request.repo,
                    "reason": "unregistered_repo",
                },
            )
        try:
            resolved = await self._tenant_git_workspace_client.resolve_workspace(credential)
        except TenantGitWorkspaceError as exc:
            raise UnprocessableEntityError(
                message=str(exc),
                details={
                    "org": exc.org,
                    "repo": exc.repo,
                    "reason": exc.reason,
                },
            ) from exc
        return resolved.path

    async def _resolve_spec_app_target(self, request: SpecWaveStartRequest) -> tuple[str, str]:
        """Use supplied app org/repo, or the single admitted fleet repo for the meta programme."""
        supplied_org = (request.org or "").strip()
        supplied_repo = (request.repo or "").strip()
        if bool(supplied_org) != bool(supplied_repo):
            raise UnprocessableEntityError(
                message="org and repo must both be supplied or both omitted",
                details={"reason": "incomplete_app_repo"},
            )
        try:
            ref = self._meta_pr_intake.parse_url(request.meta_pr_url)
        except ValueError as exc:
            raise ValidationError(
                message=str(exc),
                field_errors={"meta_pr_url": str(exc)},
            ) from exc
        try:
            async with self._postgres_service.transaction() as session:
                programme = await self._programme_repository.get_by_meta_org_repo(
                    session, org=ref.owner, repo=ref.repo
                )
        except ValueError as exc:
            raise UnprocessableEntityError(
                message=str(exc),
                details={"reason": "ambiguous_programme_meta"},
            ) from exc
        if programme is None:
            if supplied_org and supplied_repo:
                return supplied_org, supplied_repo
            raise UnprocessableEntityError(
                message="No programme matches the meta PR repository",
                details={
                    "reason": "programme_not_found_for_meta",
                    "meta_org": ref.owner,
                    "meta_repo": ref.repo,
                },
            )
        admitted = await self._tenant_service.list_admitted_repos(programme.tenant_id)
        app_repos = [
            row
            for row in admitted
            if not (row.org == programme.meta_org and row.repo == programme.meta_repo)
        ]
        if supplied_org and supplied_repo:
            if not any(row.org == supplied_org and row.repo == supplied_repo for row in app_repos):
                raise UnprocessableEntityError(
                    message="org/repo is not an admitted fleet repo for this programme",
                    details={
                        "reason": "not_admitted_repo",
                        "org": supplied_org,
                        "repo": supplied_repo,
                    },
                )
            return supplied_org, supplied_repo
        if len(app_repos) == 0:
            raise UnprocessableEntityError(
                message="Programme has no admitted app repo; admit one on Fleet",
                details={"reason": "no_admitted_repo"},
            )
        if len(app_repos) > 1:
            raise UnprocessableEntityError(
                message="Multiple admitted app repos; specify org and repo",
                details={
                    "reason": "ambiguous_app_repo",
                    "repos": [f"{row.org}/{row.repo}" for row in app_repos],
                },
            )
        return app_repos[0].org, app_repos[0].repo

    def _require_resolved_spec_target(self, request: SpecWaveStartRequest) -> tuple[str, str]:
        org = request.org
        repo = request.repo
        if org is None or repo is None:
            raise UnprocessableEntityError(
                message="org and repo must both be supplied or both omitted",
                details={"reason": "incomplete_app_repo"},
            )
        return org, repo

    async def _refuse_spec_target_is_meta(self, *, org: str, repo: str) -> None:
        """REQ-07 — spec org/repo is the app repo, never the programme meta."""
        programme = await self._find_programme_for_app_repo(org, repo)
        if programme is None:
            return
        if org == programme.meta_org and repo == programme.meta_repo:
            raise UnprocessableEntityError(
                message="spec org/repo must be an app repo, not the programme meta repo",
                details={
                    "org": org,
                    "repo": repo,
                    "reason": "spec_target_is_meta_repo",
                },
            )

    async def _require_meta_pr_onboarded(self, programme_id: UUID, meta_pr_url: str) -> None:
        """Spec start requires an admitted meta PR when a programme is bound."""
        try:
            ref = self._meta_pr_intake.parse_url(meta_pr_url)
        except ValueError:
            return
        async with self._postgres_service.transaction() as session:
            by_url = await self._programme_meta_pr_repository.get_by_programme_and_url(
                session, programme_id=programme_id, html_url=meta_pr_url.strip()
            )
            by_number = await self._programme_meta_pr_repository.get_by_programme_and_number(
                session, programme_id=programme_id, number=ref.pr_number
            )
        if by_url is None and by_number is None:
            raise UnprocessableEntityError(
                message="Meta PR is not onboarded for this programme",
                details={"reason": "meta_pr_not_onboarded"},
            )

    async def _find_programme_for_app_repo(
        self, org: str, repo: str
    ) -> Optional[ProgrammeReadModel]:
        credential = await self._tenant_service.get_workspace_credential_for_repo(
            org=org, repo=repo
        )
        if credential is None:
            return None
        async with self._postgres_service.transaction() as session:
            return await self._programme_repository.get_by_tenant_id(session, credential.tenant_id)

    async def _resolve_spec_workspace_paths(self, request: SpecWaveStartRequest) -> tuple[str, str]:
        """Honor explicit existing dirs; resolve omitted paths via tenant/programme."""
        app_path = request.workspace_path
        meta_path = request.meta_workspace_path
        if app_path:
            self._require_existing_directory(app_path, field="workspace_path")
        if meta_path:
            self._require_existing_directory(meta_path, field="meta_workspace_path")
        if app_path and meta_path:
            return app_path, meta_path

        org, repo = self._require_resolved_spec_target(request)
        credential = await self._tenant_service.get_workspace_credential_for_repo(
            org=org,
            repo=repo,
        )
        if credential is None:
            raise UnprocessableEntityError(
                message=(
                    "workspace paths omitted and org/repo is not Tenant-registered; "
                    "refusing to guess a workspace"
                ),
                details={
                    "org": org,
                    "repo": repo,
                    "reason": "unregistered_repo",
                },
            )
        if not app_path:
            try:
                resolved = await self._tenant_git_workspace_client.resolve_workspace(credential)
            except TenantGitWorkspaceError as exc:
                raise UnprocessableEntityError(
                    message=str(exc),
                    details={
                        "org": exc.org,
                        "repo": exc.repo,
                        "reason": exc.reason,
                    },
                ) from exc
            app_path = resolved.path
        if not meta_path:
            programme, pat = await self._load_programme_pat(credential.tenant_id)
            meta_credential = TenantWorkspaceCredential(
                tenant_id=programme.tenant_id,
                workspace_root=programme.workspace_root,
                pat=pat,
                org=programme.meta_org,
                repo=programme.meta_repo,
            )
            try:
                resolved_meta = await self._tenant_git_workspace_client.resolve_workspace(
                    meta_credential
                )
            except TenantGitWorkspaceError as exc:
                raise UnprocessableEntityError(
                    message=str(exc),
                    details={
                        "org": exc.org,
                        "repo": exc.repo,
                        "reason": exc.reason,
                    },
                ) from exc
            meta_path = resolved_meta.path
        return app_path, meta_path

    async def _load_programme_pat(self, tenant_id: UUID) -> tuple[ProgrammeReadModel, str]:
        async with self._postgres_service.transaction() as session:
            programme = await self._programme_repository.get_by_tenant_id(session, tenant_id)
            if programme is None:
                raise UnprocessableEntityError(
                    message="No programme for tenant; cannot resolve spec workspaces",
                    details={"tenant_id": str(tenant_id), "reason": "programme_missing"},
                )
            pat = await self._programme_repository.get_pat(session, programme.id)
            if pat is None or not pat.strip():
                raise UnprocessableEntityError(
                    message="Programme PAT missing; cannot resolve meta workspace",
                    details={"reason": "programme_pat_missing"},
                )
            return programme, pat

    async def _resolve_spec_runner_model(self, request: SpecWaveStartRequest) -> tuple[str, str]:
        runner = request.runner
        model_id = request.model_id
        if runner and model_id:
            return runner, model_id
        org, repo = self._require_resolved_spec_target(request)
        defaults = await self._spec_lane_defaults(org=org, repo=repo)
        resolved_runner = runner or (defaults.runner_id.strip() if defaults else "")
        resolved_model = model_id or (
            defaults.model_id.strip() if defaults is not None and defaults.model_id else ""
        )
        if not resolved_runner or not resolved_model:
            raise UnprocessableEntityError(
                message="lane_defaults[spec] is empty; refusing to invent runner or model",
                details={
                    "reason": "empty_spec_lane_defaults",
                    "org": org,
                    "repo": repo,
                },
            )
        return resolved_runner, resolved_model

    async def _spec_lane_defaults(self, *, org: str, repo: str) -> Optional[LaneRunnerDefault]:
        programme = await self._find_programme_for_app_repo(org, repo)
        if programme is None:
            return None
        return programme.lane_defaults.defaults.get(LaneType.SPEC)

    async def _require_spec_cap01(
        self,
        meta_accept: MetaPrAcceptResult,
        *,
        forge_client: Optional[ForgeClient] = None,
    ) -> None:
        result = await self._checkpoint_evidence.evaluate(
            PRD_IMPACT_ACCEPTANCE_CHECKPOINT_ID,
            CheckpointPrRef(
                owner=meta_accept.meta_owner,
                repo=meta_accept.meta_repo,
                number=meta_accept.meta_pr_number,
            ),
            forge_client=forge_client,
        )
        if result.verdict != CheckpointVerdictType.SATISFIED:
            raise UnprocessableEntityError(
                message="CAP-01 prd-impact-acceptance is not satisfied",
                details={
                    "reason": "cap01_not_satisfied",
                    "verdict": result.verdict.value,
                    "stale_reason": result.stale_reason,
                    "missing_items": [m.model_dump(mode="json") for m in result.missing_items],
                },
            )

    async def start_spec_wave(self, request: SpecWaveStartRequest) -> WaveStartResponse:
        """Spec-lane start: resolve binds, CAP-01 fail-closed, then enqueue."""
        org, repo = await self._resolve_spec_app_target(request)
        request = request.model_copy(update={"org": org, "repo": repo})
        await self._refuse_spec_target_is_meta(org=org, repo=repo)
        workspace_path, meta_workspace_path = await self._resolve_spec_workspace_paths(request)
        programme = await self._find_programme_for_app_repo(org, repo)
        if programme is not None:
            await self._require_meta_pr_onboarded(programme.id, request.meta_pr_url)
        programme_forge: Optional[ForgeClient] = None
        if programme is not None:
            programme_forge = await self._forge_client_factory.for_programme(programme.id)
        try:
            try:
                meta_accept = await self._meta_pr_intake.accept(
                    meta_pr_url=request.meta_pr_url,
                    expected_initiative_id=request.initiative_id,
                    forge_client=programme_forge,
                )
            except PydanticValidationError as exc:
                self.logger.warning(
                    "Meta PR accept-gate rejected invalid payload",
                    meta_pr_url=request.meta_pr_url,
                    error=str(exc),
                )
                raise ValidationError(
                    message=f"meta PR payload invalid: {exc}",
                    field_errors={"meta_pr_url": "invalid pull request payload"},
                ) from exc
            except ValueError as exc:
                self.logger.warning(
                    "Meta PR accept-gate validation failed",
                    meta_pr_url=request.meta_pr_url,
                    initiative_id=request.initiative_id,
                    error=str(exc),
                )
                raise ValidationError(
                    message=str(exc),
                    field_errors={"meta_pr_url": str(exc)},
                ) from exc
            except httpx.HTTPError as exc:
                self.logger.error(
                    "Meta PR accept-gate forge failure", error=str(exc), exc_info=True
                )
                raise ServiceUnavailableError(
                    service_name="forge",
                    message="Unable to resolve meta_pr_url for spec accept-gate",
                ) from exc

            initiative_id = meta_accept.derived_initiative_id
            if initiative_id is None:
                raise ValidationError(
                    message="meta PR accept-gate did not derive an initiative id",
                    field_errors={"meta_pr_url": "initiative_id missing"},
                )
            await self._require_spec_cap01(meta_accept, forge_client=programme_forge)
            wave_id = request.wave_id.strip() if request.wave_id else SPEC_DEFAULT_WAVE_ID
            start_node = request.start_node or SPEC_DEFAULT_START_NODE
            branch_slug = request.branch_slug or SPEC_DEFAULT_BRANCH_SLUG
            runner, model_id = await self._resolve_spec_runner_model(request)
            targeting = request.as_targeting_fields(
                initiative_id=initiative_id,
                wave_id=wave_id,
                branch_slug=branch_slug,
                start_node=start_node,
                runner=runner,
                model_id=model_id,
                org=org,
                repo=repo,
            )
            ticket = (
                str(request.ticket_id).strip()
                if request.ticket_id is not None and str(request.ticket_id).strip()
                else f"{initiative_id}:{wave_id}"
            )
            return await self._enqueue_wave(
                targeting,
                initiative_id=initiative_id,
                wave_id=wave_id,
                issue_number=request.issue_number,
                ticket=ticket,
                workspace_path=workspace_path,
                meta_accept=meta_accept,
                meta_workspace_path=meta_workspace_path,
                prior_run_id=None,
                lane="spec",
                head_ref=request.head_branch(initiative_id),
            )
        finally:
            if programme_forge is not None:
                await programme_forge.close()

    async def start_closeout_wave(self, request: CloseoutWaveStartRequest) -> WaveStartResponse:
        """Pass-2 closeout start: fixed Enter-at learning-extract; required PR bind."""
        self._require_existing_directory(request.workspace_path, field="workspace_path")
        initiative_id, wave_id, issue_number, ticket = self._resolve_ticket_identity(
            ticket_id=request.ticket_id,
            initiative_id=request.initiative_id,
            wave_id=request.wave_id,
            issue_number=request.issue_number,
        )
        head_ref = await self._resolve_closeout_pr_head(request)
        # branch_slug is non-binding for publish; derive for job payload only.
        payload_slug = branch_slug_from_head_ref(
            head_ref,
            initiative_id=initiative_id,
            wave_id=wave_id,
        )
        if request.branch_slug is not None and request.branch_slug != payload_slug:
            self.logger.info(
                "Closeout branch_slug ignored for publish head (PR head is SSOT)",
                pr_number=request.pr_number,
                branch_slug=request.branch_slug,
                head_ref=head_ref,
                derived_slug=payload_slug,
            )
        targeting = request.as_targeting_fields(branch_slug=payload_slug)
        return await self._enqueue_wave(
            targeting,
            initiative_id=initiative_id,
            wave_id=wave_id,
            issue_number=issue_number,
            ticket=ticket,
            workspace_path=request.workspace_path,
            meta_accept=None,
            meta_workspace_path=None,
            prior_run_id=request.prior_run_id,
            lane="closeout",
            head_ref=head_ref,
        )

    async def _resolve_closeout_pr_head(self, request: CloseoutWaveStartRequest) -> str:
        """Resolve publish head from the open wave PR (SSOT for Pass-2)."""
        try:
            async with self._forge_client_factory.session_for_repo(
                request.org, request.repo
            ) as forge:
                pr = await forge.get_pull_request(
                    request.org,
                    request.repo,
                    request.pr_number,
                )
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code if exc.response is not None else None
            if status == 404:
                raise ValidationError(
                    message=f"wave PR #{request.pr_number} not found",
                    field_errors={"pr_number": "not_found"},
                ) from exc
            self.logger.error(
                "Closeout PR fetch failed",
                pr_number=request.pr_number,
                status_code=status,
                error=str(exc),
                exc_info=True,
            )
            raise ServiceUnavailableError(
                service_name="forge",
                message="Unable to resolve wave PR for closeout head bind",
            ) from exc
        except httpx.HTTPError as exc:
            self.logger.error(
                "Closeout PR fetch forge failure",
                pr_number=request.pr_number,
                error=str(exc),
                exc_info=True,
            )
            raise ServiceUnavailableError(
                service_name="forge",
                message="Unable to resolve wave PR for closeout head bind",
            ) from exc

        state = (pr.state or "").strip().lower()
        if state != "open":
            raise ValidationError(
                message=f"wave PR #{request.pr_number} must be open (got {state!r})",
                field_errors={"pr_number": "must_be_open"},
            )
        head_ref = (pr.head.ref or "").strip()
        if not head_ref:
            raise ValidationError(
                message=f"wave PR #{request.pr_number} has empty head.ref",
                field_errors={"pr_number": "missing_head_ref"},
            )
        base_ref = (pr.base.ref or "").strip()
        if base_ref != request.base_branch:
            raise ValidationError(
                message=(
                    f"wave PR #{request.pr_number} base {base_ref!r} does not match "
                    f"request base_branch {request.base_branch!r}"
                ),
                field_errors={"base_branch": "mismatch"},
            )
        self.logger.info(
            "Closeout publish head resolved from wave PR",
            pr_number=request.pr_number,
            head_ref=head_ref,
            base_ref=base_ref,
        )
        return head_ref

    async def _enqueue_wave(
        self,
        request: WaveStartTargetingFields,
        *,
        initiative_id: str,
        wave_id: str,
        issue_number: Optional[int],
        ticket: str,
        workspace_path: Optional[str],
        meta_accept: Optional[MetaPrAcceptResult],
        meta_workspace_path: Optional[str],
        prior_run_id: Optional[UUID],
        lane: str,
        head_ref: Optional[str] = None,
    ) -> WaveStartResponse:
        if head_ref is None:
            _ = request.head_branch()
        else:
            # Closeout: publish head is PR-bound; slug formula must not invent a head.
            _ = head_ref.strip()
            if not _:
                raise ValidationError(
                    message="head_ref must be non-empty when provided",
                    field_errors={"head_ref": "required"},
                )

        try:
            handoff_root = self._orchestration.require_handoff_root()
        except ValueError as exc:
            raise UnprocessableEntityError(
                message=str(exc),
                details={"config_key": "GATEFLOW_HANDOFF_ROOT"},
            ) from exc

        try:
            self._workflow_engine.require_orchestrated_skill(request.start_node)
        except ValueError as exc:
            raise ValidationError(
                message=str(exc),
                field_errors={"start_node": str(exc)},
            ) from exc

        for node_id in request.node_dispatch:
            try:
                self._workflow_engine.require_orchestrated_skill(node_id)
            except ValueError as exc:
                raise ValidationError(
                    message=str(exc),
                    field_errors={"node_dispatch": str(exc)},
                ) from exc

        dispatch_plan = request.build_dispatch_plan()
        slot_result = await self._slot_validator.validate_for_run(
            runner_ids=[request.runner],
            notifier_id=self._orchestration.notifier,
            runner_config_keys={request.runner: "runner"},
            notifier_config_key="GATEFLOW_NOTIFIER",
        )
        if not slot_result.ok:
            raise UnprocessableEntityError(
                message="Required adapter is not implemented or unknown",
                details={
                    "failures": [
                        failure.model_dump(mode="json") for failure in slot_result.failures
                    ]
                },
            )

        delivery_id = f"api-wave-start-{uuid4()}"
        try:
            async with self._postgres_service.transaction() as session:
                if prior_run_id is not None:
                    prior = await self._run_repository.get_run(session, prior_run_id)
                    if prior is None:
                        raise ValidationError(
                            message="prior_run_id does not exist",
                            field_errors={"prior_run_id": "unknown run"},
                        )

                active = await self._run_repository.find_active_run(
                    session,
                    org=request.org,
                    repo=request.repo,
                )
                if active is not None:
                    raise ConflictError(
                        message=(f"Active run already exists for {request.org}/{request.repo}"),
                        details={
                            "existing_run_id": str(active.id),
                            "precondition_id": (WavePreconditionIdType.NO_CONCURRENT_RUN.value),
                        },
                    )

                run = await self._run_repository.create_run(
                    session,
                    RunCreate(
                        org=request.org,
                        repo=request.repo,
                        tenant_id=(
                            await self._require_tenant_id_for_repo(
                                org=request.org, repo=request.repo
                            )
                        ),
                        status_type=RunStatusType.ACTIVE,
                        pr_number=request.pr_number,
                        issue_number=issue_number,
                        initiative_id=initiative_id,
                        wave_id=wave_id,
                        meta_pr_url=meta_accept.meta_pr_url if meta_accept else None,
                        meta_head_sha=meta_accept.meta_head_sha if meta_accept else None,
                    ),
                )
                if run.id is None:
                    raise RuntimeError("Created run missing id")
                run_id = run.id
                handoff_path = self._define_handoff_baton(handoff_root, str(run_id))
                updated = await self._run_repository.update_run(
                    session,
                    run_id,
                    RunUpdate(handoff_path=handoff_path),
                )
                if updated is not None:
                    run = updated
                await self._metrics_emitter.record_api_trigger(
                    session,
                    run_id,
                    initiative_id=initiative_id,
                    wave_id=wave_id,
                )
                job_payload = WaveStartJobPayload(
                    delivery_id=delivery_id,
                    event_type=API_TRIGGER_EVENT,
                    run_id=str(run.id),
                    org=request.org,
                    repo=request.repo,
                    initiative_id=initiative_id,
                    wave_id=wave_id,
                    ticket_id=ticket,
                    branch_slug=request.branch_slug,
                    base_branch=request.base_branch,
                    start_node=request.start_node,
                    dispatch_plan=dispatch_plan,
                    pr_number=request.pr_number,
                    issue_number=issue_number,
                    workspace_path=workspace_path,
                    handoff_path=handoff_path,
                    trigger_source="api",
                    meta_pr_url=meta_accept.meta_pr_url if meta_accept else None,
                    meta_head_sha=meta_accept.meta_head_sha if meta_accept else None,
                    meta_workspace_path=meta_workspace_path if meta_accept else None,
                    prior_run_id=str(prior_run_id) if prior_run_id is not None else None,
                    lane=lane,
                    head_ref=head_ref.strip() if head_ref else None,
                    force_harness_recheck=(
                        request.force_harness_recheck
                        if isinstance(request, ImplementWaveStartRequest)
                        else False
                    ),
                )
                job = await self._job_repository.enqueue(
                    session,
                    JobCreate(
                        status_type=JobStatusType.PENDING,
                        delivery_id=delivery_id,
                        payload=job_payload.to_job_payload_document(),
                    ),
                )
        except (ConflictError, ValidationError, UnprocessableEntityError):
            raise
        except (SQLAlchemyError, OSError) as exc:
            self.logger.error("Wave start persist failed", error=str(exc), exc_info=True)
            raise ServiceUnavailableError(
                service_name="postgres",
                message="Unable to persist wave start run or job",
            ) from exc

        self.logger.info(
            "Wave start accepted",
            run_id=str(run.id),
            job_id=str(job.id),
            initiative_id=initiative_id,
            wave_id=wave_id,
            start_node=request.start_node,
            runner=request.runner,
            model_id=request.model_id,
            lane=lane,
            closeout_enter_at=CLOSEOUT_START_NODE if lane == "closeout" else None,
            meta_pr_url=meta_accept.meta_pr_url if meta_accept else None,
            prior_run_id=str(prior_run_id) if prior_run_id is not None else None,
        )
        return WaveStartResponse(
            run_id=str(run.id),
            job_id=str(job.id),
            status=RunStatusType.ACTIVE.value,
        )

    def _define_handoff_baton(self, handoff_root: str, run_id: str) -> str:
        """Create `{root}/{run_id}/handoff.md` and return absolute path."""
        baton_dir = Path(handoff_root) / run_id
        baton_dir.mkdir(parents=True, exist_ok=True)
        baton_path = baton_dir / "handoff.md"
        if not baton_path.exists():
            baton_path.write_text("", encoding="utf-8")
        return str(baton_path.resolve())

    def _require_existing_directory(self, path: str, *, field: str) -> None:
        candidate = Path(path)
        if not candidate.is_dir():
            raise ValidationError(
                message=f"{field} must be an existing directory",
                field_errors={field: "not an existing directory"},
            )

    def _resolve_ticket_identity(
        self,
        *,
        ticket_id: str,
        initiative_id: str,
        wave_id: str,
        issue_number: Optional[int],
    ) -> tuple[str, str, Optional[int], str]:
        """Resolve initiative/wave for lane starts after implement gate checks."""
        ticket = ticket_id
        resolved_issue = issue_number

        if ":" in ticket:
            parsed_initiative, parsed_wave = ticket.split(":", 1)
            if parsed_initiative != initiative_id or parsed_wave != wave_id:
                raise ValidationError(
                    message=(
                        "Dual identity disagree: ticket metadata does not match "
                        "initiative_id/wave_id"
                    ),
                    details={
                        "ticket_id": ticket,
                        "initiative_id": initiative_id,
                        "wave_id": wave_id,
                    },
                )
        elif ticket.isdigit():
            resolved_issue = resolved_issue if resolved_issue is not None else int(ticket)
        else:
            raise ValidationError(
                message="Unresolvable ticket_id for dual identity agreement check",
                details={"ticket_id": ticket},
            )

        return initiative_id, wave_id, resolved_issue, ticket

    async def _apply_implement_in_progress(
        self,
        *,
        org: str,
        repo: str,
        ticket: str,
        issue_number: Optional[int],
    ) -> None:
        """REQ-04: board In Progress before implement enqueue; idempotent when already set."""
        board_ticket_id: Optional[str] = None
        if ticket.isdigit():
            board_ticket_id = ticket
        elif issue_number is not None:
            board_ticket_id = str(issue_number)
        if board_ticket_id is None:
            raise UnprocessableEntityError(
                message="ticket_id must resolve to a numeric board ticket for implement-start",
                details={"ticket_id": ticket},
            )
        existing = await self._board_service.update_ticket_status(
            board_ticket_id,
            BoardTicketStatusUpdateRequest(
                org=org,
                repo=repo,
                column="In Progress",
            ),
        )
        if existing.column == "In Progress":
            self.logger.info(
                "Implement-start board In Progress (idempotent)",
                ticket_id=board_ticket_id,
                column=existing.column,
            )
        else:
            self.logger.info(
                "Implement-start applied board In Progress",
                ticket_id=board_ticket_id,
                column=existing.column,
            )

    async def _require_tenant_id_for_repo(self, *, org: str, repo: str) -> UUID:
        """Resolve tenant_id for RunSchema attribution (ADR-016)."""
        credential = await self._tenant_service.get_workspace_credential_for_repo(
            org=org, repo=repo
        )
        if credential is None:
            raise UnprocessableEntityError(
                message="No tenant registration for org/repo — cannot attribute run",
                details={"org": org, "repo": repo, "reason": "tenant_not_registered"},
            )
        return credential.tenant_id


def get_wave_start_service() -> WaveStartService:
    from src.di.dependency_container import provide_service

    return provide_service(WaveStartService)
