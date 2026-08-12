"""Programme validate-then-create, list, and tenant_admin attach (INIT-GATEFLOW-014 W1)."""

import secrets
import shutil
from pathlib import Path
from uuid import UUID, uuid4

from injector import inject

from src.business_services.auth_identity_service import AuthIdentityService
from src.business_services.base_business_service import BaseBusinessService
from src.configs.orchestration_settings import OrchestrationSettings
from src.database.postgres.repository.programme_repository import ProgrammeRepository
from src.database.postgres.repository.tenant_repository import TenantRepository
from src.database.postgres.repository.user_identity_repository import UserIdentityRepository
from src.engine.catalogue_parser import CatalogueParseError, parse_candidates
from src.exceptions.app_exceptions import (
    NotFoundError,
    UnprocessableEntityError,
)
from src.infra_services.github_pat_probe import GithubPatProbe
from src.infra_services.postgres_service import PostgresService
from src.infra_services.tenant_git_workspace_client import (
    TenantGitWorkspaceClient,
    TenantGitWorkspaceError,
)
from src.models.programme_models import (
    AttachTenantAdminRequest,
    AttachTenantAdminResponse,
    ProgrammeCreateResult,
    ProgrammeLaneDefaultsDocument,
    ProgrammeLaneDefaultsUpdateRequest,
    ProgrammeOnboardRequest,
    ProgrammeReadModel,
)
from src.models.role_types import RoleType
from src.models.tenant_git_workspace_models import TenantWorkspaceCredential
from src.utils.password_hashing import hash_password


class ProgrammeService(BaseBusinessService):
    """Own Programme lifecycle for platform_admin callers."""

    @inject
    def __init__(
        self,
        postgres_service: PostgresService,
        programme_repository: ProgrammeRepository,
        tenant_repository: TenantRepository,
        user_identity_repository: UserIdentityRepository,
        auth_identity_service: AuthIdentityService,
        github_pat_probe: GithubPatProbe,
        tenant_git_workspace_client: TenantGitWorkspaceClient,
    ) -> None:
        super().__init__()
        self._postgres_service = postgres_service
        self._programme_repository = programme_repository
        self._tenant_repository = tenant_repository
        self._user_identity_repository = user_identity_repository
        self._auth_identity_service = auth_identity_service
        self._github_pat_probe = github_pat_probe
        self._git_client = tenant_git_workspace_client
        self._orchestration = OrchestrationSettings.get_instance()

    async def validate_then_create(self, request: ProgrammeOnboardRequest) -> ProgrammeCreateResult:
        """PAT probe + meta clone/parse before any durable Programme/Tenant write."""
        org = request.meta_org.strip()
        repo = request.meta_repo.strip()
        ref = request.meta_ref.strip() if request.meta_ref and request.meta_ref.strip() else None
        workspace_root = self._orchestration.workspace_root
        pat = request.github_pat

        probe = await self._github_pat_probe.verify_read_access(pat, org, repo)
        if not probe.ok:
            self.logger.warning(
                "Programme validation rejected",
                reason="pat_probe_failed",
                org=org,
                repo=repo,
                probe_reason=probe.reason,
            )
            raise UnprocessableEntityError(
                message="GitHub PAT failed read probe for programme meta",
                details={"reason": "pat_probe_failed", "probe_reason": probe.reason},
            )

        placeholder_tenant_id = uuid4()
        credential = TenantWorkspaceCredential(
            tenant_id=placeholder_tenant_id,
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
            self.logger.warning(
                "Programme validation rejected",
                reason=exc.reason,
                org=org,
                repo=repo,
            )
            raise UnprocessableEntityError(
                message=str(exc),
                details={"reason": exc.reason, "org": org, "repo": repo},
            ) from exc

        meta_root = Path(workspace_root) / org / repo
        try:
            candidates = parse_candidates(meta_root, org=org)
        except CatalogueParseError as exc:
            if not existed_before and target.exists():
                shutil.rmtree(target, ignore_errors=True)
            self.logger.warning(
                "Programme validation rejected",
                reason=exc.reason,
                org=org,
                repo=repo,
            )
            raise UnprocessableEntityError(
                message=str(exc),
                details={"reason": exc.reason},
            ) from exc

        async with self._postgres_service.transaction() as session:
            tenant = await self._tenant_repository.create_tenant(
                session,
                name=f"programme:{request.name.strip()}",
                pat=pat,
                bearer_token=secrets.token_urlsafe(32),
                workspace_root=workspace_root,
                repos=[],
                board=None,
            )
            programme = await self._programme_repository.create_programme(
                session,
                name=request.name.strip(),
                tenant_id=tenant.tenant_id,
                github_pat=pat,
                workspace_root=workspace_root,
                meta_org=org,
                meta_repo=repo,
                meta_ref=ref,
                github_app_id=None,
                github_installation_id=None,
                lane_defaults=ProgrammeLaneDefaultsDocument(),
            )

        self.logger.info(
            "Programme created",
            programme_id=str(programme.id),
            tenant_id=str(tenant.tenant_id),
        )
        return ProgrammeCreateResult(
            programme_id=programme.id,
            tenant_id=tenant.tenant_id,
            repo_catalogue=candidates,
        )

    async def list_programmes(self) -> list[ProgrammeReadModel]:
        async with self._postgres_service.transaction() as session:
            return await self._programme_repository.list_programmes(session)

    async def get_programme(self, programme_id: UUID) -> ProgrammeReadModel:
        async with self._postgres_service.transaction() as session:
            programme = await self._programme_repository.get_by_id(session, programme_id)
        if programme is None:
            raise NotFoundError(resource_type="programme", resource_id=programme_id)
        return programme

    async def attach_tenant_admin(
        self,
        programme_id: UUID,
        request: AttachTenantAdminRequest,
    ) -> AttachTenantAdminResponse:
        async with self._postgres_service.transaction() as session:
            programme = await self._programme_repository.get_by_id(session, programme_id)
            if programme is None:
                raise UnprocessableEntityError(
                    message="Unknown programme",
                    details={"reason": "programme_not_found", "programme_id": str(programme_id)},
                )

            existing = await self._user_identity_repository.get_by_credential_identifier(
                session, request.credential_identifier
            )
            created = False
            if existing is None:
                identity = await self._user_identity_repository.create_identity(
                    session,
                    credential_identifier=request.credential_identifier,
                    password_hash=hash_password(request.password),
                    role=RoleType.TENANT_ADMIN,
                    tenant_id=programme.tenant_id,
                )
                created = True
            else:
                if (
                    existing.role != RoleType.TENANT_ADMIN
                    or existing.tenant_id != programme.tenant_id
                ):
                    raise UnprocessableEntityError(
                        message="Credential already bound to a different identity",
                        details={"reason": "credential_conflict"},
                    )
                identity = existing
                self.logger.info(
                    "Idempotent tenant_admin re-attach",
                    programme_id=str(programme_id),
                    user_id=str(identity.id),
                )

        token = self._auth_identity_service.mint_user_jwt(
            user_id=identity.id,
            role=RoleType.TENANT_ADMIN,
            tenant_id=programme.tenant_id,
        )
        self.logger.info(
            "tenant_admin attached",
            programme_id=str(programme_id),
            user_id=str(identity.id),
            created=created,
        )
        return AttachTenantAdminResponse(
            user_id=identity.id,
            tenant_id=programme.tenant_id,
            programme_id=programme_id,
            access_token=token,
            created=created,
        )

    async def set_lane_defaults(
        self,
        programme_id: UUID,
        request: ProgrammeLaneDefaultsUpdateRequest,
    ) -> ProgrammeReadModel:
        async with self._postgres_service.transaction() as session:
            programme = await self._programme_repository.get_by_id(session, programme_id)
            if programme is None:
                raise NotFoundError(resource_type="programme", resource_id=programme_id)
            return await self._programme_repository.update_lane_defaults(
                session,
                programme_id,
                ProgrammeLaneDefaultsDocument(defaults=request.defaults),
            )


def get_programme_service() -> ProgrammeService:
    from src.di.dependency_container import provide_service

    return provide_service(ProgrammeService)
