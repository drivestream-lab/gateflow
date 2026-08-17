"""MetaPrPickerService — INIT-* meta PR list + CAP-01 + spec-run join."""

from datetime import datetime, timezone
from typing import NoReturn, Optional
from uuid import UUID

import httpx
from injector import inject
from pydantic import ValidationError as PydanticValidationError

from src.business_services.base_business_service import BaseBusinessService
from src.business_services.checkpoint_evidence_service import CheckpointEvidenceService
from src.business_services.meta_pr_intake import MetaPrIntakeService
from src.configs.redis_settings import RedisSettings
from src.database.postgres.repository.programme_meta_pr_repository import (
    ProgrammeMetaPrRepository,
)
from src.database.postgres.repository.programme_repository import ProgrammeRepository
from src.database.postgres.repository.run_store_repository import RunRepository
from src.exceptions.app_exceptions import (
    NotFoundError,
    ServiceUnavailableError,
    UnprocessableEntityError,
)
from src.infra_services.forge_client import ForgeClient, ForgeClientFactory
from src.infra_services.postgres_service import PostgresService
from src.infra_services.redis_service import RedisService
from src.models.checkpoint_models import (
    PRD_IMPACT_ACCEPTANCE_CHECKPOINT_ID,
    CheckpointPrRef,
)
from src.models.meta_pr_models import GithubPullRequestDocument
from src.models.meta_pr_picker_models import (
    MetaPrCap01ReadModel,
    MetaPrPickerCachedPage,
    MetaPrPickerCachedRow,
    MetaPrPickerItem,
    MetaPrPickerResponse,
    MetaPrSpecRunJoin,
)
from src.models.programme_meta_pr_models import MetaPrOnboardRequest
from src.models.programme_models import ProgrammeReadModel
from src.models.run_store_models import RunModel
from src.models.tenant_models import TenantResolvedContext

_GITHUB_LIST_PER_PAGE = 20
_GITHUB_LIST_MAX_PAGES = 5
META_PR_PICKER_LIMIT = 10


class MetaPrPickerService(BaseBusinessService):
    """List programme meta PRs that derive INIT-* with live CAP-01 and run join."""

    @inject
    def __init__(
        self,
        postgres_service: PostgresService,
        programme_repository: ProgrammeRepository,
        programme_meta_pr_repository: ProgrammeMetaPrRepository,
        run_repository: RunRepository,
        forge_client_factory: ForgeClientFactory,
        meta_pr_intake: MetaPrIntakeService,
        checkpoint_evidence_service: CheckpointEvidenceService,
        redis_service: RedisService,
    ) -> None:
        super().__init__()
        self._postgres_service = postgres_service
        self._programme_repository = programme_repository
        self._programme_meta_pr_repository = programme_meta_pr_repository
        self._run_repository = run_repository
        self._forge_client_factory = forge_client_factory
        self._meta_pr_intake = meta_pr_intake
        self._checkpoint_evidence = checkpoint_evidence_service
        self._redis = redis_service
        self._redis_settings = RedisSettings.get_instance()

    async def list_meta_prs(
        self,
        tenant_id: UUID,
        resolved: TenantResolvedContext,
        *,
        skip: int = 0,
        limit: int = META_PR_PICKER_LIMIT,
        refresh: bool = False,
    ) -> MetaPrPickerResponse:
        """Return the latest INIT-derived meta PRs (at most META_PR_PICKER_LIMIT).

        ``refresh=True`` skips Redis, fetches GitHub, and rewrites the cache.
        """
        if limit > META_PR_PICKER_LIMIT:
            raise UnprocessableEntityError(
                message="Meta PR picker returns at most the last 10 INIT-derived PRs",
                details={"reason": "meta_pr_picker_limit", "limit": limit},
            )
        if resolved.tenant_id != tenant_id:
            raise UnprocessableEntityError(
                message="Resolved tenant does not match path tenant_id",
                details={
                    "tenant_id": str(tenant_id),
                    "resolved_tenant_id": str(resolved.tenant_id),
                },
            )
        programme, runs, onboarded_urls = await self._load_programme_and_runs(tenant_id)
        owner = programme.meta_org
        repo = programme.meta_repo
        cached = (
            None if refresh else await self._read_github_page(programme.id, skip=skip, limit=limit)
        )
        if cached is not None:
            items = self._join_cached_page(cached, runs, onboarded_urls)
            self.logger.info(
                "Meta PR picker listed",
                tenant_id=str(tenant_id),
                meta_org=owner,
                meta_repo=repo,
                item_count=len(items),
                skip=skip,
                limit=limit,
                cache_hit=True,
            )
            return MetaPrPickerResponse(meta_org=owner, meta_repo=repo, items=items)

        page = await self._fetch_github_page(
            programme, owner=owner, repo=repo, tenant_id=tenant_id, skip=skip, limit=limit
        )
        await self._write_github_page(programme.id, skip=skip, limit=limit, page=page)
        items = self._join_cached_page(page, runs, onboarded_urls)
        self.logger.info(
            "Meta PR picker listed",
            tenant_id=str(tenant_id),
            meta_org=owner,
            meta_repo=repo,
            item_count=len(items),
            skip=skip,
            limit=limit,
            cache_hit=False,
            refresh=refresh,
        )
        return MetaPrPickerResponse(meta_org=owner, meta_repo=repo, items=items)

    async def list_onboarded_meta_prs(
        self,
        tenant_id: UUID,
        resolved: TenantResolvedContext,
    ) -> MetaPrPickerResponse:
        """Return admitted meta PRs only — no GitHub list."""
        self._assert_tenant(tenant_id, resolved)
        programme, runs, _urls = await self._load_programme_and_runs(tenant_id)
        async with self._postgres_service.transaction() as session:
            rows = await self._programme_meta_pr_repository.list_by_programme(session, programme.id)
        forge = await self._forge_client_factory.for_programme(programme.id)
        try:
            items: list[MetaPrPickerItem] = []
            for row in rows:
                checkpoint = await self._cap01_read_only(
                    programme.meta_org,
                    programme.meta_repo,
                    row.number,
                    forge_client=forge,
                )
                items.append(
                    MetaPrPickerItem(
                        number=row.number,
                        html_url=row.html_url,
                        title=row.title,
                        state="open",
                        merged=False,
                        initiative_id=row.initiative_id,
                        checkpoint=checkpoint,
                        spec_runs=self._join_spec_runs(
                            runs,
                            initiative_id=row.initiative_id,
                            meta_pr_url=row.html_url,
                        ),
                        onboarded=True,
                    )
                )
        finally:
            await forge.close()
        self.logger.info(
            "Onboarded meta PRs listed",
            tenant_id=str(tenant_id),
            item_count=len(items),
        )
        return MetaPrPickerResponse(
            meta_org=programme.meta_org,
            meta_repo=programme.meta_repo,
            items=items,
        )

    async def onboard_meta_pr(
        self,
        tenant_id: UUID,
        resolved: TenantResolvedContext,
        body: MetaPrOnboardRequest,
    ) -> MetaPrPickerItem:
        """Admit one INIT-* meta PR on this programme's meta repo."""
        self._assert_tenant(tenant_id, resolved)
        programme, runs, _urls = await self._load_programme_and_runs(tenant_id)
        try:
            ref = self._meta_pr_intake.parse_url(body.html_url)
        except ValueError as exc:
            raise UnprocessableEntityError(
                message=str(exc),
                details={"reason": "invalid_meta_pr_url"},
            ) from exc
        if (
            ref.owner.lower() != programme.meta_org.lower()
            or ref.repo.lower() != programme.meta_repo.lower()
        ):
            raise UnprocessableEntityError(
                message="Meta PR is not on this programme's meta repository",
                details={
                    "reason": "meta_pr_wrong_repo",
                    "meta_org": programme.meta_org,
                    "meta_repo": programme.meta_repo,
                },
            )
        forge = await self._forge_client_factory.for_programme(programme.id)
        try:
            try:
                pr = await forge.get_pull_request(ref.owner, ref.repo, ref.pr_number)
            except httpx.HTTPStatusError as exc:
                self._raise_list_forge_status(
                    exc, owner=ref.owner, repo=ref.repo, tenant_id=tenant_id
                )
            except httpx.HTTPError as exc:
                raise ServiceUnavailableError(
                    service_name="forge",
                    message="Unable to fetch meta pull request for onboard",
                ) from exc
            derived = self._meta_pr_intake.derive_initiative_id(pr)
            if derived is None:
                raise UnprocessableEntityError(
                    message="Meta PR does not derive an INIT-* initiative",
                    details={"reason": "not_init_meta_pr"},
                )
            if pr.number is None:
                raise UnprocessableEntityError(
                    message="GitHub pull request missing number",
                    details={"reason": "invalid_meta_pr"},
                )
            html_url = self._html_url(ref.owner, ref.repo, pr)
            async with self._postgres_service.transaction() as session:
                existing = await self._programme_meta_pr_repository.get_by_programme_and_number(
                    session, programme_id=programme.id, number=pr.number
                )
                if existing is None:
                    existing = await self._programme_meta_pr_repository.create(
                        session,
                        programme_id=programme.id,
                        html_url=html_url,
                        number=pr.number,
                        initiative_id=derived,
                        title=pr.title,
                    )
                    created = True
                else:
                    created = False
            checkpoint = await self._cap01_read_only(
                programme.meta_org,
                programme.meta_repo,
                pr.number,
                forge_client=forge,
            )
        finally:
            await forge.close()
        self.logger.info(
            "Meta PR onboarded",
            tenant_id=str(tenant_id),
            html_url=html_url,
            created=created,
        )
        return MetaPrPickerItem(
            number=existing.number,
            html_url=existing.html_url,
            title=existing.title,
            state=pr.state,
            merged=pr.merged,
            initiative_id=existing.initiative_id,
            checkpoint=checkpoint,
            spec_runs=self._join_spec_runs(
                runs,
                initiative_id=existing.initiative_id,
                meta_pr_url=existing.html_url,
            ),
            onboarded=True,
        )

    def _assert_tenant(self, tenant_id: UUID, resolved: TenantResolvedContext) -> None:
        if resolved.tenant_id != tenant_id:
            raise UnprocessableEntityError(
                message="Resolved tenant does not match path tenant_id",
                details={
                    "tenant_id": str(tenant_id),
                    "resolved_tenant_id": str(resolved.tenant_id),
                },
            )

    def _cache_key(self, programme_id: UUID, *, skip: int, limit: int) -> str:
        return f"{self._redis_settings.prefix}meta_pr_picker:v1:{programme_id}:{skip}:{limit}"

    async def _read_github_page(
        self, programme_id: UUID, *, skip: int, limit: int
    ) -> Optional[MetaPrPickerCachedPage]:
        raw = await self._redis.get(
            self._cache_key(programme_id, skip=skip, limit=limit), as_json=True
        )
        if raw is None:
            return None
        try:
            return MetaPrPickerCachedPage.model_validate(raw)
        except PydanticValidationError:
            self.logger.warning(
                "Meta PR picker cache payload invalid; fetching GitHub",
                programme_id=str(programme_id),
                skip=skip,
                limit=limit,
            )
            return None

    async def _write_github_page(
        self,
        programme_id: UUID,
        *,
        skip: int,
        limit: int,
        page: MetaPrPickerCachedPage,
    ) -> None:
        await self._redis.set(
            self._cache_key(programme_id, skip=skip, limit=limit),
            page.model_dump(mode="json"),
            ttl=self._redis_settings.meta_pr_picker_ttl,
        )

    async def _fetch_github_page(
        self,
        programme: ProgrammeReadModel,
        *,
        owner: str,
        repo: str,
        tenant_id: UUID,
        skip: int,
        limit: int,
    ) -> MetaPrPickerCachedPage:
        forge = await self._forge_client_factory.for_programme(programme.id)
        try:
            try:
                candidates = await self._collect_init_prs(
                    forge, owner, repo, skip=skip, limit=limit
                )
            except httpx.HTTPStatusError as exc:
                self._raise_list_forge_status(exc, owner=owner, repo=repo, tenant_id=tenant_id)
            except httpx.HTTPError as exc:
                self.logger.error(
                    "Meta PR list forge failure",
                    meta_org=owner,
                    meta_repo=repo,
                    tenant_id=str(tenant_id),
                    error=str(exc),
                    exc_info=True,
                )
                raise ServiceUnavailableError(
                    service_name="forge",
                    message="Unable to list programme meta pull requests",
                ) from exc

            rows: list[MetaPrPickerCachedRow] = []
            for pr, initiative_id in candidates:
                if pr.number is None:
                    raise UnprocessableEntityError(
                        message="GitHub pull-request list item missing number",
                        details={"meta_org": owner, "meta_repo": repo},
                    )
                html_url = self._html_url(owner, repo, pr)
                checkpoint = await self._cap01_read_only(owner, repo, pr.number, forge_client=forge)
                rows.append(
                    MetaPrPickerCachedRow(
                        number=pr.number,
                        html_url=html_url,
                        title=pr.title,
                        state=pr.state,
                        merged=pr.merged,
                        initiative_id=initiative_id,
                        checkpoint=checkpoint,
                    )
                )
        finally:
            await forge.close()
        return MetaPrPickerCachedPage(meta_org=owner, meta_repo=repo, items=rows)

    def _join_cached_page(
        self,
        page: MetaPrPickerCachedPage,
        runs: list[RunModel],
        onboarded_urls: set[str],
    ) -> list[MetaPrPickerItem]:
        items: list[MetaPrPickerItem] = []
        for row in page.items:
            items.append(
                MetaPrPickerItem(
                    number=row.number,
                    html_url=row.html_url,
                    title=row.title,
                    state=row.state,
                    merged=row.merged,
                    initiative_id=row.initiative_id,
                    checkpoint=row.checkpoint,
                    spec_runs=self._join_spec_runs(
                        runs,
                        initiative_id=row.initiative_id,
                        meta_pr_url=row.html_url,
                    ),
                    onboarded=row.html_url in onboarded_urls,
                )
            )
        return items

    def _raise_list_forge_status(
        self,
        exc: httpx.HTTPStatusError,
        *,
        owner: str,
        repo: str,
        tenant_id: UUID,
    ) -> NoReturn:
        status_code = exc.response.status_code
        self.logger.error(
            "Meta PR list forge failure",
            meta_org=owner,
            meta_repo=repo,
            tenant_id=str(tenant_id),
            status_code=status_code,
            error=str(exc),
            exc_info=True,
        )
        if status_code == 404:
            raise NotFoundError(
                resource_type="repository",
                resource_id=f"{owner}/{repo}",
                message="Programme meta repository was not found",
            ) from exc
        if status_code in {401, 403}:
            raise UnprocessableEntityError(
                message="Programme GitHub credential cannot list meta pull requests",
                details={
                    "reason": "meta_repo_forbidden",
                    "meta_org": owner,
                    "meta_repo": repo,
                    "status_code": status_code,
                },
            ) from exc
        raise ServiceUnavailableError(
            service_name="forge",
            message="Unable to list programme meta pull requests",
            details={"status_code": status_code},
        ) from exc

    async def _load_programme_and_runs(
        self, tenant_id: UUID
    ) -> tuple[ProgrammeReadModel, list[RunModel], set[str]]:
        async with self._postgres_service.transaction() as session:
            programme = await self._programme_repository.get_by_tenant_id(session, tenant_id)
            if programme is None:
                raise NotFoundError(resource_type="programme", resource_id=str(tenant_id))
            runs = await self._run_repository.list_runs(
                session,
                tenant_id=tenant_id,
                limit=200,
            )
            tracked = await self._programme_meta_pr_repository.list_by_programme(
                session, programme.id
            )
        return programme, runs, {row.html_url for row in tracked}

    async def _collect_init_prs(
        self,
        forge_client: ForgeClient,
        owner: str,
        repo: str,
        *,
        skip: int,
        limit: int,
    ) -> list[tuple[GithubPullRequestDocument, str]]:
        needed = skip + limit
        collected: list[tuple[GithubPullRequestDocument, str]] = []
        for page in range(1, _GITHUB_LIST_MAX_PAGES + 1):
            batch = await forge_client.list_pull_requests(
                owner,
                repo,
                state="all",
                per_page=_GITHUB_LIST_PER_PAGE,
                page=page,
            )
            for pr in batch:
                if pr.number is None:
                    raise UnprocessableEntityError(
                        message="GitHub pull-request list item missing number",
                        details={"meta_org": owner, "meta_repo": repo},
                    )
                derived = self._meta_pr_intake.derive_initiative_id(pr)
                if derived is None:
                    continue
                collected.append((pr, derived))
            if len(batch) < _GITHUB_LIST_PER_PAGE or len(collected) >= needed:
                break
        return collected[skip : skip + limit]

    async def _cap01_read_only(
        self,
        owner: str,
        repo: str,
        number: int,
        *,
        forge_client: ForgeClient,
    ) -> MetaPrCap01ReadModel:
        pr_ref = CheckpointPrRef(owner=owner, repo=repo, number=number)
        try:
            result = await self._checkpoint_evidence.evaluate_read_only(
                PRD_IMPACT_ACCEPTANCE_CHECKPOINT_ID,
                pr_ref,
                forge_client=forge_client,
            )
        except NotFoundError:
            result = CheckpointEvidenceService._could_not_verify(
                PRD_IMPACT_ACCEPTANCE_CHECKPOINT_ID,
                pr_ref,
                datetime.now(timezone.utc),
                None,
            )
        return MetaPrCap01ReadModel(
            checkpoint_id=result.checkpoint_id,
            verdict=result.verdict,
            checked_sha=result.checked_sha,
            stale_reason=result.stale_reason,
            missing_items=list(result.missing_items),
        )

    @staticmethod
    def _join_spec_runs(
        runs: list[RunModel],
        *,
        initiative_id: str,
        meta_pr_url: str,
    ) -> list[MetaPrSpecRunJoin]:
        """Latest spec-lane run per (org, repo) for this meta_pr_url. No initiative-only fallback."""
        latest: dict[tuple[str, str], RunModel] = {}
        for run in runs:
            url = (run.meta_pr_url or "").strip()
            if not url or url != meta_pr_url or run.id is None:
                continue
            if run.initiative_id and run.initiative_id != initiative_id:
                continue
            key = (run.org, run.repo)
            if key not in latest:
                latest[key] = run
        return [
            MetaPrSpecRunJoin(org=org, repo=repo, spec_run_id=str(run.id))
            for (org, repo), run in latest.items()
        ]

    @staticmethod
    def _html_url(owner: str, repo: str, pr: GithubPullRequestDocument) -> str:
        if pr.html_url and pr.html_url.strip():
            return pr.html_url.strip()
        if pr.number is None:
            raise UnprocessableEntityError(
                message="GitHub pull-request list item missing number",
                details={"meta_org": owner, "meta_repo": repo},
            )
        return f"https://github.com/{owner}/{repo}/pull/{pr.number}"


def get_meta_pr_picker_service() -> MetaPrPickerService:
    from src.di.dependency_container import provide_service

    return provide_service(MetaPrPickerService)
