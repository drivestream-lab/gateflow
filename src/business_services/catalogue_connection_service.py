"""Meta-catalogue connection: connect, catalogue, selection, setup (INIT-013).

Renamed from ProgrammeOnboardingService (INIT-GATEFLOW-014 W1 AF-1).
"""

import shutil
from pathlib import Path
from uuid import UUID

from injector import inject

from src.business_services.base_business_service import BaseBusinessService
from src.database.postgres.repository.run_store_repository import RunRepository
from src.database.postgres.repository.tenant_repository import TenantRepository
from src.engine.catalogue_parser import CatalogueParseError, parse_candidates
from src.exceptions.app_exceptions import (
    NotFoundError,
    UnauthorizedError,
    UnprocessableEntityError,
)
from src.infra_services.github_pat_probe import GithubPatProbe
from src.infra_services.launchpad_status_client import (
    LaunchpadStatusClient,
    LaunchpadStatusError,
)
from src.infra_services.postgres_service import PostgresService
from src.infra_services.tenant_git_workspace_client import (
    TenantGitWorkspaceClient,
    TenantGitWorkspaceError,
)
from src.models.programme_catalogue_models import ProgrammeCatalogueResponse
from src.models.programme_connection_models import (
    ProgrammeCatalogueRefreshResponse,
    ProgrammeConnectRequest,
    ProgrammeConnectResponse,
    ProgrammeConnectionReadModel,
)
from src.models.programme_readiness_models import (
    ProgrammeReadinessRefreshRequest,
    ProgrammeReadinessRefreshResponse,
    ReadinessSourceType,
)
from src.models.programme_selection_models import (
    ProgrammeDeselectRequest,
    ProgrammeDeselectResponse,
    ProgrammeRepoAdmitOutcomeType,
    ProgrammeRepoAdmitResult,
    ProgrammeSelectRequest,
    ProgrammeSelectResponse,
)
from src.models.tenant_git_workspace_models import TenantWorkspaceCredential
from src.models.tenant_models import TenantRepoProbeFailure, TenantRepoRef, TenantResolvedContext


class CatalogueConnectionService(BaseBusinessService):
    """Connect tenant to meta-repo catalogue, select/setup, and status readiness."""

    @inject
    def __init__(
        self,
        postgres_service: PostgresService,
        tenant_repository: TenantRepository,
        tenant_git_workspace_client: TenantGitWorkspaceClient,
        github_pat_probe: GithubPatProbe,
        run_repository: RunRepository,
        launchpad_status_client: LaunchpadStatusClient,
    ) -> None:
        super().__init__()
        self._postgres_service = postgres_service
        self._tenant_repository = tenant_repository
        self._git_client = tenant_git_workspace_client
        self._github_pat_probe = github_pat_probe
        self._run_repository = run_repository
        self._status_client = launchpad_status_client

    async def connect_programme(
        self,
        tenant_id: UUID,
        request: ProgrammeConnectRequest,
        *,
        resolved: TenantResolvedContext,
    ) -> ProgrammeConnectResponse:
        self._assert_tenant_match(tenant_id, resolved)
        org = request.org.strip()
        repo = request.repo.strip()
        ref = request.ref.strip() if request.ref is not None and request.ref.strip() else None

        async with self._postgres_service.transaction() as session:
            auth = await self._tenant_repository.get_tenant_workspace_auth(session, tenant_id)
            if auth is None:
                raise NotFoundError(resource_type="tenant", resource_id=tenant_id)
            workspace_root, pat = auth

        credential = TenantWorkspaceCredential(
            tenant_id=tenant_id,
            workspace_root=workspace_root,
            pat=pat,
            org=org,
            repo=repo,
        )
        target = Path(workspace_root) / org / repo
        existed_before = target.exists()
        try:
            await self._git_client.resolve_workspace(credential, ref=ref)
        except TenantGitWorkspaceError as exc:
            if not existed_before and target.exists():
                shutil.rmtree(target, ignore_errors=True)
            self.logger.error(
                "Programme connect git failed",
                tenant_id=str(tenant_id),
                org=org,
                repo=repo,
                reason=exc.reason,
            )
            raise UnprocessableEntityError(
                message=str(exc),
                details={
                    "org": org,
                    "repo": repo,
                    "reason": exc.reason,
                },
            ) from exc

        async with self._postgres_service.transaction() as session:
            connection = await self._tenant_repository.upsert_programme_connection(
                session,
                tenant_id=tenant_id,
                org=org,
                repo=repo,
                ref=ref,
            )

        self.logger.info(
            "Programme connected",
            tenant_id=str(tenant_id),
            org=org,
            repo=repo,
            ref=ref,
        )
        return ProgrammeConnectResponse(connection=connection)

    async def get_catalogue(
        self,
        tenant_id: UUID,
        *,
        resolved: TenantResolvedContext,
    ) -> ProgrammeCatalogueResponse:
        self._assert_tenant_match(tenant_id, resolved)

        async with self._postgres_service.transaction() as session:
            connection = await self._tenant_repository.get_programme_connection(session, tenant_id)
            auth = await self._tenant_repository.get_tenant_workspace_auth(session, tenant_id)

        if connection is None:
            raise UnprocessableEntityError(
                message="Tenant has no programme connection",
                details={"reason": "programme_not_connected"},
            )
        if auth is None:
            raise NotFoundError(resource_type="tenant", resource_id=tenant_id)

        workspace_root, _pat = auth
        meta_root = Path(workspace_root) / connection.org / connection.repo
        try:
            candidates = parse_candidates(meta_root, org=connection.org)
        except CatalogueParseError as exc:
            self.logger.warning(
                "Catalogue parse rejected",
                tenant_id=str(tenant_id),
                reason=exc.reason,
            )
            raise UnprocessableEntityError(
                message=str(exc),
                details={"reason": exc.reason},
            ) from exc

        self.logger.info(
            "Catalogue read",
            tenant_id=str(tenant_id),
            candidate_count=len(candidates),
        )
        return ProgrammeCatalogueResponse(
            programme_org=connection.org,
            candidates=candidates,
        )

    async def get_connection(
        self,
        tenant_id: UUID,
        *,
        resolved: TenantResolvedContext,
    ) -> ProgrammeConnectionReadModel:
        self._assert_tenant_match(tenant_id, resolved)
        async with self._postgres_service.transaction() as session:
            connection = await self._tenant_repository.get_programme_connection(session, tenant_id)
        if connection is None:
            raise UnprocessableEntityError(
                message="Tenant has no programme connection",
                details={"reason": "programme_not_connected"},
            )
        return connection

    async def refresh_catalogue(
        self,
        tenant_id: UUID,
        *,
        resolved: TenantResolvedContext,
    ) -> ProgrammeCatalogueRefreshResponse:
        """Re-sync programme meta checkout; never mutate selections or readiness (REQ-24/25)."""
        self._assert_tenant_match(tenant_id, resolved)

        async with self._postgres_service.transaction() as session:
            connection = await self._tenant_repository.get_programme_connection(session, tenant_id)
            auth = await self._tenant_repository.get_tenant_workspace_auth(session, tenant_id)

        if connection is None:
            raise UnprocessableEntityError(
                message="Tenant has no programme connection",
                details={"reason": "programme_not_connected"},
            )
        if auth is None:
            raise NotFoundError(resource_type="tenant", resource_id=tenant_id)

        workspace_root, pat = auth
        credential = TenantWorkspaceCredential(
            tenant_id=tenant_id,
            workspace_root=workspace_root,
            pat=pat,
            org=connection.org,
            repo=connection.repo,
        )
        try:
            await self._git_client.resolve_workspace(credential, ref=connection.ref)
        except TenantGitWorkspaceError as exc:
            self.logger.error(
                "Programme catalogue refresh git failed",
                tenant_id=str(tenant_id),
                org=connection.org,
                repo=connection.repo,
                reason=exc.reason,
            )
            raise UnprocessableEntityError(
                message=str(exc),
                details={
                    "org": connection.org,
                    "repo": connection.repo,
                    "reason": exc.reason,
                },
            ) from exc

        async with self._postgres_service.transaction() as session:
            updated = await self._tenant_repository.upsert_programme_connection(
                session,
                tenant_id=tenant_id,
                org=connection.org,
                repo=connection.repo,
                ref=connection.ref,
            )

        self.logger.info(
            "Programme catalogue refreshed",
            tenant_id=str(tenant_id),
            org=updated.org,
            repo=updated.repo,
            ref=updated.ref,
        )
        return ProgrammeCatalogueRefreshResponse(connection=updated)

    async def select_repos(
        self,
        tenant_id: UUID,
        request: ProgrammeSelectRequest,
        *,
        resolved: TenantResolvedContext,
    ) -> ProgrammeSelectResponse:
        """Admit catalogue-gated repos; PAT probe; setup each new admit independently."""
        self._assert_tenant_match(tenant_id, resolved)

        async with self._postgres_service.transaction() as session:
            connection = await self._tenant_repository.get_programme_connection(session, tenant_id)
            auth = await self._tenant_repository.get_tenant_workspace_auth(session, tenant_id)
            active = await self._tenant_repository.list_tenant_repos(session, tenant_id)

        if connection is None:
            raise UnprocessableEntityError(
                message="Tenant has no programme connection",
                details={"reason": "programme_not_connected"},
            )
        if auth is None:
            raise NotFoundError(resource_type="tenant", resource_id=tenant_id)

        workspace_root, pat = auth
        meta_root = Path(workspace_root) / connection.org / connection.repo
        try:
            candidates = parse_candidates(meta_root, org=connection.org)
        except CatalogueParseError as exc:
            raise UnprocessableEntityError(
                message=str(exc),
                details={"reason": exc.reason},
            ) from exc

        candidate_keys = {(c.org, c.repo) for c in candidates}
        requested = [TenantRepoRef(org=r.org.strip(), repo=r.repo.strip()) for r in request.repos]
        out_of_catalogue = [r for r in requested if (r.org, r.repo) not in candidate_keys]
        if out_of_catalogue:
            self.logger.warning(
                "Select rejected out-of-catalogue repos",
                tenant_id=str(tenant_id),
                rejected_count=len(out_of_catalogue),
            )
            raise UnprocessableEntityError(
                message="One or more repos are not on the current catalogue",
                details={
                    "reason": "out_of_catalogue",
                    "repos": [r.model_dump(mode="json") for r in out_of_catalogue],
                },
            )

        active_keys = {(r.org, r.repo) for r in active}
        new_admits = [r for r in requested if (r.org, r.repo) not in active_keys]

        probe_failures: list[TenantRepoProbeFailure] = []
        for ref in new_admits:
            probe = await self._github_pat_probe.verify_read_access(pat, ref.org, ref.repo)
            if not probe.ok:
                probe_failures.append(
                    TenantRepoProbeFailure(
                        org=ref.org,
                        repo=ref.repo,
                        reason=probe.reason or "unknown",
                    )
                )
        if probe_failures:
            self.logger.warning(
                "Select rejected by PAT probe",
                tenant_id=str(tenant_id),
                failure_count=len(probe_failures),
            )
            raise UnprocessableEntityError(
                message="PAT failed read-access verification for one or more repos",
                details={
                    "reason": "probe_failed",
                    "failures": [f.model_dump(mode="json") for f in probe_failures],
                },
            )

        if new_admits:
            async with self._postgres_service.transaction() as session:
                await self._tenant_repository.add_tenant_repos(
                    session,
                    tenant_id=tenant_id,
                    repos=new_admits,
                    readiness_source=ReadinessSourceType.LAUNCHPAD_STATUS.value,
                )
                active = await self._tenant_repository.list_tenant_repos(session, tenant_id)

        results: list[ProgrammeRepoAdmitResult] = []
        new_keys = {(r.org, r.repo) for r in new_admits}
        meta_config_dir = str(meta_root.resolve())
        for ref in requested:
            if (ref.org, ref.repo) not in new_keys:
                results.append(
                    ProgrammeRepoAdmitResult(
                        org=ref.org,
                        repo=ref.repo,
                        outcome=ProgrammeRepoAdmitOutcomeType.ALREADY_SELECTED,
                    )
                )
                continue

            credential = TenantWorkspaceCredential(
                tenant_id=tenant_id,
                workspace_root=workspace_root,
                pat=pat,
                org=ref.org,
                repo=ref.repo,
            )
            target = Path(workspace_root) / ref.org / ref.repo
            existed_before = target.exists()
            try:
                await self._git_client.resolve_workspace(credential)
            except TenantGitWorkspaceError as exc:
                if not existed_before and target.exists():
                    shutil.rmtree(target, ignore_errors=True)
                self.logger.warning(
                    "Programme repo setup failed",
                    tenant_id=str(tenant_id),
                    org=ref.org,
                    repo=ref.repo,
                    reason=exc.reason,
                )
                results.append(
                    ProgrammeRepoAdmitResult(
                        org=ref.org,
                        repo=ref.repo,
                        outcome=ProgrammeRepoAdmitOutcomeType.SETUP_FAILED,
                        reason=exc.reason,
                    )
                )
                continue

            status_result = await self._run_status_for_repo(
                tenant_id=tenant_id,
                org=ref.org,
                repo=ref.repo,
                repo_workspace=str(target.resolve()),
                meta_config_dir=meta_config_dir,
            )
            results.append(status_result)

        self.logger.info(
            "Programme repos selected",
            tenant_id=str(tenant_id),
            requested_count=len(requested),
            new_admit_count=len(new_admits),
        )
        return ProgrammeSelectResponse(results=results, active_repos=active)

    async def _run_status_for_repo(
        self,
        *,
        tenant_id: UUID,
        org: str,
        repo: str,
        repo_workspace: str,
        meta_config_dir: str,
    ) -> ProgrammeRepoAdmitResult:
        """Inspect-only status after successful setup; isolates failures (REQ-17/19/20)."""
        try:
            verdict = await self._status_client.inspect_status(
                repo_workspace=repo_workspace,
                meta_config_dir=meta_config_dir,
                org=org,
                repo=repo,
            )
        except LaunchpadStatusError as exc:
            self.logger.warning(
                "Programme repo status tool failure",
                tenant_id=str(tenant_id),
                org=org,
                repo=repo,
                reason=exc.reason,
            )
            return ProgrammeRepoAdmitResult(
                org=org,
                repo=repo,
                outcome=ProgrammeRepoAdmitOutcomeType.STATUS_FAILED,
                reason=exc.reason,
            )

        if verdict.ready:
            async with self._postgres_service.transaction() as session:
                await self._tenant_repository.set_harness_verified(
                    session, org=org, repo=repo, verified=True
                )
            self.logger.info(
                "Programme repo status ok",
                tenant_id=str(tenant_id),
                org=org,
                repo=repo,
            )
            return ProgrammeRepoAdmitResult(
                org=org,
                repo=repo,
                outcome=ProgrammeRepoAdmitOutcomeType.OK,
            )

        self.logger.warning(
            "Programme repo status not ready",
            tenant_id=str(tenant_id),
            org=org,
            repo=repo,
            reason=verdict.reason,
        )
        return ProgrammeRepoAdmitResult(
            org=org,
            repo=repo,
            outcome=ProgrammeRepoAdmitOutcomeType.STATUS_FAILED,
            reason=verdict.reason or "repo_not_ready",
        )

    async def refresh_readiness(
        self,
        tenant_id: UUID,
        request: ProgrammeReadinessRefreshRequest,
        *,
        resolved: TenantResolvedContext,
    ) -> ProgrammeReadinessRefreshResponse:
        """On-demand status refresh for launchpad_status-sourced repos (REQ-23)."""
        self._assert_tenant_match(tenant_id, resolved)
        org = request.org.strip()
        repo = request.repo.strip()

        async with self._postgres_service.transaction() as session:
            connection = await self._tenant_repository.get_programme_connection(session, tenant_id)
            auth = await self._tenant_repository.get_tenant_workspace_auth(session, tenant_id)
            active = await self._tenant_repository.list_tenant_repos(session, tenant_id)
            source_raw = await self._tenant_repository.get_readiness_source(
                session, org=org, repo=repo
            )

        if connection is None:
            raise UnprocessableEntityError(
                message="Tenant has no programme connection",
                details={"reason": "programme_not_connected"},
            )
        if auth is None:
            raise NotFoundError(resource_type="tenant", resource_id=tenant_id)
        if not any(r.org == org and r.repo == repo for r in active):
            raise UnprocessableEntityError(
                message="Repo is not on the tenant active list",
                details={"reason": "not_selected", "org": org, "repo": repo},
            )
        if source_raw != ReadinessSourceType.LAUNCHPAD_STATUS.value:
            raise UnprocessableEntityError(
                message="Readiness refresh is only for launchpad_status-sourced repos",
                details={
                    "reason": "readiness_source_not_status",
                    "org": org,
                    "repo": repo,
                    "readiness_source": source_raw,
                },
            )

        workspace_root, _pat = auth
        repo_workspace = Path(workspace_root) / org / repo
        meta_config_dir = Path(workspace_root) / connection.org / connection.repo
        if not repo_workspace.is_dir():
            raise UnprocessableEntityError(
                message="Repo workspace checkout missing for status refresh",
                details={"reason": "workspace_path_missing", "org": org, "repo": repo},
            )

        try:
            verdict = await self._status_client.inspect_status(
                repo_workspace=str(repo_workspace.resolve()),
                meta_config_dir=str(meta_config_dir.resolve()),
                org=org,
                repo=repo,
            )
        except LaunchpadStatusError as exc:
            raise UnprocessableEntityError(
                message=str(exc),
                details={"reason": exc.reason, "org": org, "repo": repo},
            ) from exc

        async with self._postgres_service.transaction() as session:
            await self._tenant_repository.set_harness_verified(
                session, org=org, repo=repo, verified=verdict.ready
            )

        self.logger.info(
            "Programme repo readiness refreshed",
            tenant_id=str(tenant_id),
            org=org,
            repo=repo,
            harness_verified=verdict.ready,
            verdict_type=verdict.verdict_type.value,
        )
        return ProgrammeReadinessRefreshResponse(
            org=org,
            repo=repo,
            readiness_source=ReadinessSourceType.LAUNCHPAD_STATUS,
            harness_verified=verdict.ready,
            verdict_type=verdict.verdict_type,
            reason=verdict.reason,
        )

    async def deselect_repo(
        self,
        tenant_id: UUID,
        request: ProgrammeDeselectRequest,
        *,
        resolved: TenantResolvedContext,
    ) -> ProgrammeDeselectResponse:
        """Remove active-list membership; block when ACTIVE run exists (REQ-26/27)."""
        self._assert_tenant_match(tenant_id, resolved)
        org = request.org.strip()
        repo = request.repo.strip()

        async with self._postgres_service.transaction() as session:
            active_before = await self._tenant_repository.list_tenant_repos(session, tenant_id)
            if not any(r.org == org and r.repo == repo for r in active_before):
                raise UnprocessableEntityError(
                    message="Repo is not on the tenant active list",
                    details={"reason": "not_selected", "org": org, "repo": repo},
                )
            active_run = await self._run_repository.find_active_run(session, org, repo)
            if active_run is not None:
                self.logger.warning(
                    "Deselect blocked by active run",
                    tenant_id=str(tenant_id),
                    org=org,
                    repo=repo,
                    run_id=str(active_run.id),
                )
                raise UnprocessableEntityError(
                    message="Cannot deselect repo while an ACTIVE run exists",
                    details={
                        "reason": "active_run",
                        "org": org,
                        "repo": repo,
                        "run_id": str(active_run.id),
                    },
                )
            removed = await self._tenant_repository.remove_tenant_repo(
                session, tenant_id=tenant_id, org=org, repo=repo
            )
            if not removed:
                raise UnprocessableEntityError(
                    message="Repo is not on the tenant active list",
                    details={"reason": "not_selected", "org": org, "repo": repo},
                )
            active = await self._tenant_repository.list_tenant_repos(session, tenant_id)

        self.logger.info(
            "Programme repo deselected",
            tenant_id=str(tenant_id),
            org=org,
            repo=repo,
        )
        return ProgrammeDeselectResponse(org=org, repo=repo, active_repos=active)

    @staticmethod
    def _assert_tenant_match(tenant_id: UUID, resolved: TenantResolvedContext) -> None:
        if resolved.tenant_id != tenant_id:
            raise UnauthorizedError(message="Tenant token does not match path tenant_id")


def get_catalogue_connection_service() -> CatalogueConnectionService:
    from src.di.dependency_container import provide_service

    return provide_service(CatalogueConnectionService)
