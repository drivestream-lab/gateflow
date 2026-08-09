"""Tenant registry repository (INIT-GATEFLOW-012 W0 / INIT-GATEFLOW-013 W0)."""

from datetime import datetime, UTC
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.postgres.repository.base_repository import BasePostgresRepository
from src.database.postgres.schema.tenant_schema import (
    TenantProgrammeConnectionSchema,
    TenantRepoSchema,
    TenantSchema,
    TenantUserSchema,
)
from src.di.qualified_types import PostgresSessionFactory
from src.models.programme_connection_models import ProgrammeConnectionReadModel
from src.models.tenant_git_workspace_models import TenantWorkspaceCredential
from src.models.tenant_models import (
    TenantBoardDefault,
    TenantReadModel,
    TenantRepoRef,
    TenantResolvedContext,
)


class TenantRepository(BasePostgresRepository[TenantSchema]):
    """Persist tenants / repos / users; read DTOs never include pat."""

    def __init__(self, session_factory: PostgresSessionFactory) -> None:
        super().__init__(TenantSchema, session_factory)

    def _board_from_row(self, row: TenantSchema) -> Optional[TenantBoardDefault]:
        if row.board_project_owner is None or row.board_project_number is None:
            return None
        return TenantBoardDefault(
            project_owner=row.board_project_owner,
            project_number=row.board_project_number,
        )

    async def _repos_for_tenant(
        self, session: AsyncSession, tenant_id: UUID
    ) -> list[TenantRepoRef]:
        stmt = (
            select(TenantRepoSchema)
            .where(TenantRepoSchema.tenant_id == tenant_id)
            .order_by(TenantRepoSchema.org.asc(), TenantRepoSchema.repo.asc())
        )
        result = await session.execute(stmt)
        return [TenantRepoRef(org=r.org, repo=r.repo) for r in result.scalars().all()]

    def _to_read_model(self, row: TenantSchema, repos: list[TenantRepoRef]) -> TenantReadModel:
        return TenantReadModel(
            tenant_id=row.id,
            name=row.name,
            repos=repos,
            workspace_root=row.workspace_root,
            board=self._board_from_row(row),
        )

    async def create_tenant(
        self,
        session: AsyncSession,
        *,
        name: str,
        pat: str,
        bearer_token: str,
        workspace_root: str,
        repos: list[TenantRepoRef],
        board: Optional[TenantBoardDefault],
    ) -> TenantReadModel:
        row = TenantSchema(
            name=name,
            pat=pat,
            bearer_token=bearer_token,
            workspace_root=workspace_root,
            board_project_owner=board.project_owner if board else None,
            board_project_number=board.project_number if board else None,
        )
        session.add(row)
        await session.flush()
        for ref in repos:
            session.add(
                TenantRepoSchema(
                    tenant_id=row.id,
                    org=ref.org,
                    repo=ref.repo,
                    harness_verified=False,
                )
            )
        await session.flush()
        return self._to_read_model(row, list(repos))

    async def get_by_id(self, session: AsyncSession, tenant_id: UUID) -> Optional[TenantReadModel]:
        row = await session.get(TenantSchema, tenant_id)
        if row is None:
            return None
        repos = await self._repos_for_tenant(session, tenant_id)
        return self._to_read_model(row, repos)

    async def list_tenants(self, session: AsyncSession) -> list[TenantReadModel]:
        stmt = select(TenantSchema).order_by(TenantSchema.name.asc())
        result = await session.execute(stmt)
        rows = list(result.scalars().all())
        out: list[TenantReadModel] = []
        for row in rows:
            repos = await self._repos_for_tenant(session, row.id)
            out.append(self._to_read_model(row, repos))
        return out

    async def resolve_tenant_by_token(
        self, session: AsyncSession, bearer_token: str
    ) -> Optional[TenantResolvedContext]:
        stmt = select(TenantSchema).where(TenantSchema.bearer_token == bearer_token)
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return TenantResolvedContext(tenant_id=row.id, name=row.name)

    async def attach_user(
        self,
        session: AsyncSession,
        *,
        tenant_id: UUID,
        identity: str,
    ) -> None:
        session.add(TenantUserSchema(tenant_id=tenant_id, identity=identity))
        await session.flush()

    async def is_user_attached(
        self,
        session: AsyncSession,
        *,
        tenant_id: UUID,
        identity: str,
    ) -> bool:
        stmt = select(TenantUserSchema.id).where(
            TenantUserSchema.tenant_id == tenant_id,
            TenantUserSchema.identity == identity,
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_board_default(
        self, session: AsyncSession, tenant_id: UUID
    ) -> Optional[TenantBoardDefault]:
        row = await session.get(TenantSchema, tenant_id)
        if row is None:
            return None
        return self._board_from_row(row)

    async def find_workspace_credential_by_org_repo(
        self,
        session: AsyncSession,
        *,
        org: str,
        repo: str,
    ) -> Optional[TenantWorkspaceCredential]:
        """Return tenant + stored PAT for a registered org/repo (REQ-11 lookup).

        Read/list DTOs never include PAT; this internal shape is for git auth only.
        Ambiguous multi-tenant registration of the same org/repo fails closed.
        """
        stmt = (
            select(TenantSchema, TenantRepoSchema)
            .join(TenantRepoSchema, TenantRepoSchema.tenant_id == TenantSchema.id)
            .where(TenantRepoSchema.org == org, TenantRepoSchema.repo == repo)
            .order_by(TenantSchema.id.asc())
            .limit(2)
        )
        result = await session.execute(stmt)
        rows = list(result.all())
        if not rows:
            return None
        if len(rows) > 1:
            raise ValueError(
                f"Ambiguous tenant registration for {org}/{repo}: multiple tenants match"
            )
        tenant_row, repo_row = rows[0]
        return TenantWorkspaceCredential(
            tenant_id=tenant_row.id,
            workspace_root=tenant_row.workspace_root,
            pat=tenant_row.pat,
            org=repo_row.org,
            repo=repo_row.repo,
        )

    async def get_harness_verified(
        self,
        session: AsyncSession,
        *,
        org: str,
        repo: str,
    ) -> Optional[bool]:
        """Return cached harness_verified for org/repo, or None if unregistered."""
        stmt = (
            select(TenantRepoSchema)
            .where(TenantRepoSchema.org == org, TenantRepoSchema.repo == repo)
            .order_by(TenantRepoSchema.tenant_id.asc())
            .limit(2)
        )
        result = await session.execute(stmt)
        rows = list(result.scalars().all())
        if not rows:
            return None
        if len(rows) > 1:
            raise ValueError(
                f"Ambiguous tenant registration for {org}/{repo}: multiple tenants match"
            )
        return bool(rows[0].harness_verified)

    async def set_harness_verified(
        self,
        session: AsyncSession,
        *,
        org: str,
        repo: str,
        verified: bool,
    ) -> None:
        """Persist harness_verified for a registered org/repo (REQ-22 cache)."""
        stmt = (
            select(TenantRepoSchema)
            .where(TenantRepoSchema.org == org, TenantRepoSchema.repo == repo)
            .order_by(TenantRepoSchema.tenant_id.asc())
            .limit(2)
        )
        result = await session.execute(stmt)
        rows = list(result.scalars().all())
        if not rows:
            raise ValueError(f"No tenant_repos row for {org}/{repo}")
        if len(rows) > 1:
            raise ValueError(
                f"Ambiguous tenant registration for {org}/{repo}: multiple tenants match"
            )
        rows[0].harness_verified = verified
        await session.flush()

    async def get_tenant_workspace_auth(
        self,
        session: AsyncSession,
        tenant_id: UUID,
    ) -> Optional[tuple[str, str]]:
        """Return (workspace_root, pat) for a tenant — never for API responses."""
        row = await session.get(TenantSchema, tenant_id)
        if row is None:
            return None
        return row.workspace_root, row.pat

    def _connection_to_read(
        self, row: TenantProgrammeConnectionSchema
    ) -> ProgrammeConnectionReadModel:
        return ProgrammeConnectionReadModel(
            tenant_id=row.tenant_id,
            org=row.org,
            repo=row.repo,
            ref=row.ref,
            last_synced_at=row.last_synced_at,
        )

    async def get_programme_connection(
        self,
        session: AsyncSession,
        tenant_id: UUID,
    ) -> Optional[ProgrammeConnectionReadModel]:
        stmt = select(TenantProgrammeConnectionSchema).where(
            TenantProgrammeConnectionSchema.tenant_id == tenant_id
        )
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return self._connection_to_read(row)

    async def upsert_programme_connection(
        self,
        session: AsyncSession,
        *,
        tenant_id: UUID,
        org: str,
        repo: str,
        ref: Optional[str],
        last_synced_at: Optional[datetime] = None,
    ) -> ProgrammeConnectionReadModel:
        """Insert or update the single programme connection for a tenant (REQ-28)."""
        synced = last_synced_at or datetime.now(UTC)
        stmt = select(TenantProgrammeConnectionSchema).where(
            TenantProgrammeConnectionSchema.tenant_id == tenant_id
        )
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            row = TenantProgrammeConnectionSchema(
                tenant_id=tenant_id,
                org=org,
                repo=repo,
                ref=ref,
                last_synced_at=synced,
            )
            session.add(row)
        else:
            row.org = org
            row.repo = repo
            row.ref = ref
            row.last_synced_at = synced
        await session.flush()
        return self._connection_to_read(row)
