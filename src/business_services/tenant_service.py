"""Tenant registry business service (INIT-GATEFLOW-012 W0 / INIT-GATEFLOW-013 W1)."""

import secrets
from pathlib import Path
from typing import Optional
from uuid import UUID

from injector import inject

from src.business_services.base_business_service import BaseBusinessService
from src.database.postgres.repository.tenant_repository import TenantRepository
from src.exceptions.app_exceptions import (
    NotFoundError,
    UnauthorizedError,
    UnprocessableEntityError,
    ValidationError,
)
from src.infra_services.postgres_service import PostgresService
from src.models.programme_readiness_models import ReadinessSourceType
from src.models.programme_connection_models import ProgrammeConnectionReadModel
from src.models.tenant_git_workspace_models import TenantWorkspaceCredential
from src.models.tenant_models import (
    TenantListResponse,
    TenantReadModel,
    TenantRegisterRequest,
    TenantRegisterResponse,
    TenantResolvedContext,
    TenantUserAttachRequest,
    TenantUserAttachResponse,
)


class TenantService(BaseBusinessService):
    """Register / attach / read tenants; PAT never returned on any response."""

    @inject
    def __init__(
        self,
        postgres_service: PostgresService,
        tenant_repository: TenantRepository,
    ) -> None:
        super().__init__()
        self._postgres_service = postgres_service
        self._tenant_repository = tenant_repository

    async def register_tenant(self, request: TenantRegisterRequest) -> TenantRegisterResponse:
        if not Path(request.workspace_root).is_absolute():
            raise ValidationError(
                message="workspace_root must be an absolute path",
                field_errors={"workspace_root": "must_be_absolute"},
            )
        if request.repos:
            self.logger.warning(
                "Tenant registration rejected non-empty repos",
                repo_count=len(request.repos),
            )
            raise UnprocessableEntityError(
                message="repos is retired; admit repos via programme selection only",
                details={"reason": "repos_not_allowed"},
            )

        bearer_token = secrets.token_urlsafe(32)
        async with self._postgres_service.transaction() as session:
            read = await self._tenant_repository.create_tenant(
                session,
                name=request.name,
                pat=request.pat,
                bearer_token=bearer_token,
                workspace_root=request.workspace_root,
                repos=[],
                board=request.board,
            )

        self.logger.info(
            "Tenant registered",
            tenant_id=str(read.tenant_id),
            repo_count=len(read.repos),
        )
        return TenantRegisterResponse(
            tenant_id=read.tenant_id,
            name=read.name,
            bearer_token=bearer_token,
            repos=read.repos,
            workspace_root=read.workspace_root,
            board=read.board,
        )

    async def attach_user(
        self,
        tenant_id: UUID,
        request: TenantUserAttachRequest,
        *,
        resolved: TenantResolvedContext,
    ) -> TenantUserAttachResponse:
        if resolved.tenant_id != tenant_id:
            raise UnauthorizedError(message="Tenant token does not match path tenant_id")
        async with self._postgres_service.transaction() as session:
            existing = await self._tenant_repository.get_by_id(session, tenant_id)
            if existing is None:
                raise NotFoundError(resource_type="tenant", resource_id=tenant_id)
            await self._tenant_repository.attach_user(
                session, tenant_id=tenant_id, identity=request.identity
            )
        self.logger.info(
            "Tenant user attached",
            tenant_id=str(tenant_id),
        )
        return TenantUserAttachResponse(tenant_id=tenant_id, identity=request.identity)

    async def list_tenants(self, *, resolved: TenantResolvedContext) -> TenantListResponse:
        _ = resolved  # any valid tenant token may list (no PAT in payload)
        async with self._postgres_service.transaction() as session:
            tenants = await self._tenant_repository.list_tenants(session)
        return TenantListResponse(tenants=tenants)

    async def get_tenant(
        self,
        tenant_id: UUID,
        *,
        resolved: TenantResolvedContext,
        identity: Optional[str] = None,
    ) -> TenantReadModel:
        if resolved.tenant_id != tenant_id:
            raise UnauthorizedError(message="Tenant token does not match path tenant_id")
        async with self._postgres_service.transaction() as session:
            if identity is not None:
                attached = await self._tenant_repository.is_user_attached(
                    session, tenant_id=tenant_id, identity=identity
                )
                if not attached:
                    raise UnauthorizedError(message="Caller identity is not attached to tenant")
            read = await self._tenant_repository.get_by_id(session, tenant_id)
            if read is None:
                raise NotFoundError(resource_type="tenant", resource_id=tenant_id)
            return read

    async def get_workspace_credential_for_repo(
        self,
        *,
        org: str,
        repo: str,
    ) -> Optional[TenantWorkspaceCredential]:
        """Lookup stored PAT + workspace_root for a registered org/repo (REQ-11)."""
        try:
            async with self._postgres_service.transaction() as session:
                return await self._tenant_repository.find_workspace_credential_by_org_repo(
                    session, org=org, repo=repo
                )
        except ValueError as exc:
            raise UnprocessableEntityError(
                message=str(exc),
                details={"org": org, "repo": repo, "reason": "ambiguous_tenant_registration"},
            ) from exc

    async def get_programme_connection(
        self, tenant_id: UUID
    ) -> Optional[ProgrammeConnectionReadModel]:
        """Return programme connection for tenant, or None."""
        async with self._postgres_service.transaction() as session:
            return await self._tenant_repository.get_programme_connection(session, tenant_id)

    async def is_harness_verified(self, *, org: str, repo: str) -> bool:
        """Return True when tenant_repos.harness_verified is set (REQ-22)."""
        try:
            async with self._postgres_service.transaction() as session:
                flag = await self._tenant_repository.get_harness_verified(
                    session, org=org, repo=repo
                )
        except ValueError as exc:
            raise UnprocessableEntityError(
                message=str(exc),
                details={"org": org, "repo": repo, "reason": "ambiguous_tenant_registration"},
            ) from exc
        return bool(flag)

    async def get_readiness_source(self, *, org: str, repo: str) -> Optional[ReadinessSourceType]:
        """Return durable evaluator provenance (ADR-013); None if unregistered."""
        try:
            async with self._postgres_service.transaction() as session:
                raw = await self._tenant_repository.get_readiness_source(
                    session, org=org, repo=repo
                )
        except ValueError as exc:
            raise UnprocessableEntityError(
                message=str(exc),
                details={"org": org, "repo": repo, "reason": "ambiguous_tenant_registration"},
            ) from exc
        if raw is None:
            return None
        try:
            return ReadinessSourceType(raw)
        except ValueError:
            return ReadinessSourceType.FILESYSTEM

    async def mark_harness_verified(self, *, org: str, repo: str, verified: bool = True) -> None:
        """Cache harness readiness after a successful probe (REQ-22)."""
        try:
            async with self._postgres_service.transaction() as session:
                await self._tenant_repository.set_harness_verified(
                    session, org=org, repo=repo, verified=verified
                )
        except ValueError as exc:
            raise UnprocessableEntityError(
                message=str(exc),
                details={"org": org, "repo": repo, "reason": "harness_cache_update_failed"},
            ) from exc
        self.logger.info(
            "Tenant repo harness verified updated",
            org=org,
            repo=repo,
            harness_verified=verified,
        )

    async def resolve_tenant_by_token(self, bearer_token: str) -> Optional[TenantResolvedContext]:
        async with self._postgres_service.transaction() as session:
            return await self._tenant_repository.resolve_tenant_by_token(session, bearer_token)


def get_tenant_service() -> TenantService:
    from src.di.dependency_container import provide_service

    return provide_service(TenantService)
