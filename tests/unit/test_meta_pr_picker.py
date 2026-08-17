"""Unit tests for MetaPrPickerService (INIT-GATEFLOW-019 CAP-A)."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import httpx
import pytest

from src.business_services.meta_pr_intake import MetaPrIntakeService
from src.business_services.meta_pr_picker_service import MetaPrPickerService
from src.exceptions.app_exceptions import (
    NotFoundError,
    ServiceUnavailableError,
    UnprocessableEntityError,
)
from src.models.checkpoint_models import (
    PRD_IMPACT_ACCEPTANCE_CHECKPOINT_ID,
    CheckpointStatusResult,
    CheckpointVerdictType,
)
from src.models.meta_pr_models import GithubPullRequestDocument
from src.models.meta_pr_picker_models import (
    MetaPrCap01ReadModel,
    MetaPrPickerCachedPage,
    MetaPrPickerCachedRow,
)
from src.models.programme_meta_pr_models import MetaPrOnboardRequest, ProgrammeMetaPrReadModel
from src.models.programme_models import ProgrammeLaneDefaultsDocument, ProgrammeReadModel
from src.models.run_store_models import RunModel
from src.models.run_store_types import RunStatusType
from src.models.tenant_models import TenantResolvedContext


@asynccontextmanager
async def _txn() -> AsyncIterator[MagicMock]:
    yield MagicMock()


def _programme(tenant_id: UUID) -> ProgrammeReadModel:
    return ProgrammeReadModel(
        id=uuid4(),
        name="acme",
        tenant_id=tenant_id,
        workspace_root="/tmp/ws",
        meta_org="acme",
        meta_repo="prayog-meta",
        lane_defaults=ProgrammeLaneDefaultsDocument(),
    )


def _service(
    *,
    programme: ProgrammeReadModel,
    pulls: list[GithubPullRequestDocument],
    runs: list[RunModel],
    verdict: CheckpointVerdictType = CheckpointVerdictType.SATISFIED,
) -> tuple[MetaPrPickerService, MagicMock, MagicMock, MagicMock]:
    postgres = MagicMock()
    postgres.transaction = _txn
    programme_repo = MagicMock()
    programme_repo.get_by_tenant_id = AsyncMock(return_value=programme)
    meta_pr_repo = MagicMock()
    meta_pr_repo.list_by_programme = AsyncMock(return_value=[])
    meta_pr_repo.get_by_programme_and_number = AsyncMock(return_value=None)
    meta_pr_repo.create = AsyncMock()
    run_repo = MagicMock()
    run_repo.list_runs = AsyncMock(return_value=runs)
    forge = MagicMock()
    forge.list_pull_requests = AsyncMock(return_value=pulls)
    forge.get_pull_request = AsyncMock(return_value=pulls[0] if pulls else None)
    forge.close = AsyncMock()
    factory = MagicMock()
    factory.for_programme = AsyncMock(return_value=forge)
    intake = MetaPrIntakeService(forge_client_factory=factory)
    checkpoint = MagicMock()
    checkpoint.evaluate_read_only = AsyncMock(
        return_value=CheckpointStatusResult(
            checkpoint_id=PRD_IMPACT_ACCEPTANCE_CHECKPOINT_ID,
            owner=programme.meta_org,
            repo=programme.meta_repo,
            pr_number=1,
            verdict=verdict,
            checked_at=datetime.now(timezone.utc),
        )
    )
    checkpoint.evaluate = AsyncMock()
    redis = MagicMock()
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock(return_value=True)
    service = MetaPrPickerService(
        postgres_service=postgres,
        programme_repository=programme_repo,
        programme_meta_pr_repository=meta_pr_repo,
        run_repository=run_repo,
        forge_client_factory=factory,
        meta_pr_intake=intake,
        checkpoint_evidence_service=checkpoint,
        redis_service=redis,
    )
    return service, factory, forge, redis


@pytest.mark.asyncio
async def test_list_omits_non_init_and_joins_spec_run() -> None:
    tenant_id = uuid4()
    run_id = uuid4()
    pulls = [
        GithubPullRequestDocument(
            number=1,
            html_url="https://github.com/acme/prayog-meta/pull/1",
            title="INIT-ACME-001 intake",
            state="open",
        ),
        GithubPullRequestDocument(
            number=2,
            html_url="https://github.com/acme/prayog-meta/pull/2",
            title="chore: docs",
            state="open",
        ),
    ]
    runs = [
        RunModel(
            tenant_id=tenant_id,
            id=run_id,
            org="acme",
            repo="widget",
            status_type=RunStatusType.ACTIVE,
            initiative_id="INIT-ACME-001",
            wave_id="W0",
            meta_pr_url="https://github.com/acme/prayog-meta/pull/1",
            retry_counter=0,
            notify_pending=False,
        )
    ]
    service, _, _, _ = _service(programme=_programme(tenant_id), pulls=pulls, runs=runs)
    result = await service.list_meta_prs(
        tenant_id,
        TenantResolvedContext(tenant_id=tenant_id, name="acme"),
    )
    assert result.meta_org == "acme"
    assert result.meta_repo == "prayog-meta"
    assert len(result.items) == 1
    item = result.items[0]
    assert item.initiative_id == "INIT-ACME-001"
    assert [(row.org, row.repo, row.spec_run_id) for row in item.spec_runs] == [
        ("acme", "widget", str(run_id))
    ]
    assert item.checkpoint.verdict == CheckpointVerdictType.SATISFIED
    evaluate = service._checkpoint_evidence.evaluate
    read_only = service._checkpoint_evidence.evaluate_read_only
    assert isinstance(evaluate, AsyncMock)
    assert isinstance(read_only, AsyncMock)
    evaluate.assert_not_called()
    read_only.assert_awaited()


@pytest.mark.asyncio
async def test_list_missing_spec_run_is_none() -> None:
    tenant_id = uuid4()
    pulls = [
        GithubPullRequestDocument(
            number=9,
            html_url="https://github.com/acme/prayog-meta/pull/9",
            title="INIT-ACME-009 intake",
            state="closed",
            merged=True,
        )
    ]
    service, _, _, _ = _service(programme=_programme(tenant_id), pulls=pulls, runs=[])
    result = await service.list_meta_prs(
        tenant_id,
        TenantResolvedContext(tenant_id=tenant_id, name="acme"),
    )
    assert result.items[0].spec_runs == []
    assert result.items[0].merged is True


@pytest.mark.asyncio
async def test_list_uses_programme_forge_and_closes() -> None:
    tenant_id = uuid4()
    programme = _programme(tenant_id)
    pulls = [
        GithubPullRequestDocument(
            number=1,
            html_url="https://github.com/acme/prayog-meta/pull/1",
            title="INIT-ACME-001 intake",
            state="open",
        )
    ]
    service, factory, forge, _ = _service(programme=programme, pulls=pulls, runs=[])
    await service.list_meta_prs(
        tenant_id,
        TenantResolvedContext(tenant_id=tenant_id, name="acme"),
    )
    factory.for_programme.assert_awaited_once_with(programme.id)
    forge.close.assert_awaited()
    read_only = service._checkpoint_evidence.evaluate_read_only
    assert isinstance(read_only, AsyncMock)
    assert read_only.await_args is not None
    assert read_only.await_args.kwargs["forge_client"] is forge


def _status_error(status_code: int) -> httpx.HTTPStatusError:
    request = httpx.Request("GET", "https://api.github.com/repos/acme/prayog-meta/pulls")
    response = httpx.Response(status_code, request=request)
    return httpx.HTTPStatusError("forge status", request=request, response=response)


@pytest.mark.asyncio
async def test_list_forbidden_is_422_not_503() -> None:
    tenant_id = uuid4()
    service, _, forge, _ = _service(programme=_programme(tenant_id), pulls=[], runs=[])
    forge.list_pull_requests = AsyncMock(side_effect=_status_error(403))
    with pytest.raises(UnprocessableEntityError) as exc_info:
        await service.list_meta_prs(
            tenant_id,
            TenantResolvedContext(tenant_id=tenant_id, name="acme"),
        )
    assert exc_info.value.details["reason"] == "meta_repo_forbidden"
    forge.close.assert_awaited()


@pytest.mark.asyncio
async def test_list_missing_repo_is_404_not_503() -> None:
    tenant_id = uuid4()
    service, _, forge, _ = _service(programme=_programme(tenant_id), pulls=[], runs=[])
    forge.list_pull_requests = AsyncMock(side_effect=_status_error(404))
    with pytest.raises(NotFoundError):
        await service.list_meta_prs(
            tenant_id,
            TenantResolvedContext(tenant_id=tenant_id, name="acme"),
        )
    forge.close.assert_awaited()


@pytest.mark.asyncio
async def test_list_transient_http_is_503() -> None:
    tenant_id = uuid4()
    service, _, forge, _ = _service(programme=_programme(tenant_id), pulls=[], runs=[])
    forge.list_pull_requests = AsyncMock(side_effect=httpx.ConnectError("down"))
    with pytest.raises(ServiceUnavailableError):
        await service.list_meta_prs(
            tenant_id,
            TenantResolvedContext(tenant_id=tenant_id, name="acme"),
        )
    forge.close.assert_awaited()


def _cached_page(*, number: int = 1, initiative_id: str = "INIT-ACME-001") -> dict[str, object]:
    return MetaPrPickerCachedPage(
        meta_org="acme",
        meta_repo="prayog-meta",
        items=[
            MetaPrPickerCachedRow(
                number=number,
                html_url=f"https://github.com/acme/prayog-meta/pull/{number}",
                title=f"{initiative_id} intake",
                state="open",
                merged=False,
                initiative_id=initiative_id,
                checkpoint=MetaPrCap01ReadModel(
                    checkpoint_id=PRD_IMPACT_ACCEPTANCE_CHECKPOINT_ID,
                    verdict=CheckpointVerdictType.SATISFIED,
                ),
            )
        ],
    ).model_dump(mode="json")


@pytest.mark.asyncio
async def test_list_cache_hit_skips_github_and_rejoins() -> None:
    tenant_id = uuid4()
    run_id = uuid4()
    runs = [
        RunModel(
            tenant_id=tenant_id,
            id=run_id,
            org="acme",
            repo="widget",
            status_type=RunStatusType.ACTIVE,
            initiative_id="INIT-ACME-001",
            wave_id="W0",
            meta_pr_url="https://github.com/acme/prayog-meta/pull/1",
            retry_counter=0,
            notify_pending=False,
        )
    ]
    service, factory, forge, redis = _service(programme=_programme(tenant_id), pulls=[], runs=runs)
    redis.get = AsyncMock(return_value=_cached_page())
    result = await service.list_meta_prs(
        tenant_id,
        TenantResolvedContext(tenant_id=tenant_id, name="acme"),
    )
    assert [(row.org, row.repo, row.spec_run_id) for row in result.items[0].spec_runs] == [
        ("acme", "widget", str(run_id))
    ]
    factory.for_programme.assert_not_awaited()
    forge.list_pull_requests.assert_not_awaited()
    read_only = service._checkpoint_evidence.evaluate_read_only
    assert isinstance(read_only, AsyncMock)
    read_only.assert_not_awaited()
    redis.set.assert_not_awaited()


@pytest.mark.asyncio
async def test_list_cache_miss_writes_github_slice() -> None:
    tenant_id = uuid4()
    pulls = [
        GithubPullRequestDocument(
            number=1,
            html_url="https://github.com/acme/prayog-meta/pull/1",
            title="INIT-ACME-001 intake",
            state="open",
        )
    ]
    service, _, forge, redis = _service(programme=_programme(tenant_id), pulls=pulls, runs=[])
    result = await service.list_meta_prs(
        tenant_id,
        TenantResolvedContext(tenant_id=tenant_id, name="acme"),
    )
    assert len(result.items) == 1
    redis.set.assert_awaited()
    forge.list_pull_requests.assert_awaited()


@pytest.mark.asyncio
async def test_list_refresh_bypasses_cache_and_rewrites() -> None:
    tenant_id = uuid4()
    pulls = [
        GithubPullRequestDocument(
            number=3,
            html_url="https://github.com/acme/prayog-meta/pull/3",
            title="INIT-ACME-003 intake",
            state="open",
        )
    ]
    service, factory, forge, redis = _service(programme=_programme(tenant_id), pulls=pulls, runs=[])
    redis.get = AsyncMock(return_value=_cached_page())
    result = await service.list_meta_prs(
        tenant_id,
        TenantResolvedContext(tenant_id=tenant_id, name="acme"),
        refresh=True,
    )
    assert [item.number for item in result.items] == [3]
    redis.get.assert_not_awaited()
    factory.for_programme.assert_awaited()
    forge.list_pull_requests.assert_awaited()
    redis.set.assert_awaited()


@pytest.mark.asyncio
async def test_list_joins_spec_runs_per_repo() -> None:
    tenant_id = uuid4()
    widget_run = uuid4()
    ops_run = uuid4()
    pulls = [
        GithubPullRequestDocument(
            number=1,
            html_url="https://github.com/acme/prayog-meta/pull/1",
            title="INIT-ACME-001 intake",
            state="open",
        )
    ]
    runs = [
        RunModel(
            tenant_id=tenant_id,
            id=widget_run,
            org="acme",
            repo="widget",
            status_type=RunStatusType.ACTIVE,
            initiative_id="INIT-ACME-001",
            wave_id="W0",
            meta_pr_url="https://github.com/acme/prayog-meta/pull/1",
            retry_counter=0,
            notify_pending=False,
        ),
        RunModel(
            tenant_id=tenant_id,
            id=ops_run,
            org="acme",
            repo="ops",
            status_type=RunStatusType.ACTIVE,
            initiative_id="INIT-ACME-001",
            wave_id="W0",
            meta_pr_url="https://github.com/acme/prayog-meta/pull/1",
            retry_counter=0,
            notify_pending=False,
        ),
    ]
    service, _, _, _ = _service(programme=_programme(tenant_id), pulls=pulls, runs=runs)
    result = await service.list_meta_prs(
        tenant_id,
        TenantResolvedContext(tenant_id=tenant_id, name="acme"),
    )
    joined = {(row.org, row.repo, row.spec_run_id) for row in result.items[0].spec_runs}
    assert joined == {
        ("acme", "widget", str(widget_run)),
        ("acme", "ops", str(ops_run)),
    }


@pytest.mark.asyncio
async def test_list_caps_at_last_ten_init_prs() -> None:
    tenant_id = uuid4()
    pulls = [
        GithubPullRequestDocument(
            number=n,
            html_url=f"https://github.com/acme/prayog-meta/pull/{n}",
            title=f"INIT-ACME-{n:03d}",
            state="open",
        )
        for n in range(1, 13)
    ]
    service, _, _, _ = _service(programme=_programme(tenant_id), pulls=pulls, runs=[])
    result = await service.list_meta_prs(
        tenant_id,
        TenantResolvedContext(tenant_id=tenant_id, name="acme"),
    )
    assert [item.number for item in result.items] == list(range(1, 11))


@pytest.mark.asyncio
async def test_list_rejects_limit_over_ten() -> None:
    tenant_id = uuid4()
    service, _, _, _ = _service(programme=_programme(tenant_id), pulls=[], runs=[])
    with pytest.raises(UnprocessableEntityError) as exc_info:
        await service.list_meta_prs(
            tenant_id,
            TenantResolvedContext(tenant_id=tenant_id, name="acme"),
            limit=11,
        )
    assert exc_info.value.details.get("reason") == "meta_pr_picker_limit"


@pytest.mark.asyncio
async def test_onboard_admits_init_pr() -> None:
    tenant_id = uuid4()
    programme = _programme(tenant_id)
    pulls = [
        GithubPullRequestDocument(
            number=9,
            html_url="https://github.com/acme/prayog-meta/pull/9",
            title="INIT-ACME-009 intake",
            state="open",
        )
    ]
    service, _, forge, _ = _service(programme=programme, pulls=pulls, runs=[])
    created = ProgrammeMetaPrReadModel(
        id=uuid4(),
        programme_id=programme.id,
        html_url="https://github.com/acme/prayog-meta/pull/9",
        number=9,
        initiative_id="INIT-ACME-009",
        title="INIT-ACME-009 intake",
    )
    service._programme_meta_pr_repository.create = AsyncMock(return_value=created)
    item = await service.onboard_meta_pr(
        tenant_id,
        TenantResolvedContext(tenant_id=tenant_id, name="acme"),
        MetaPrOnboardRequest(html_url="https://github.com/acme/prayog-meta/pull/9"),
    )
    assert item.onboarded is True
    assert item.initiative_id == "INIT-ACME-009"
    forge.get_pull_request.assert_awaited()
    service._programme_meta_pr_repository.create.assert_awaited()


@pytest.mark.asyncio
async def test_onboard_rejects_wrong_meta_repo() -> None:
    tenant_id = uuid4()
    service, _, _, _ = _service(programme=_programme(tenant_id), pulls=[], runs=[])
    with pytest.raises(UnprocessableEntityError) as exc_info:
        await service.onboard_meta_pr(
            tenant_id,
            TenantResolvedContext(tenant_id=tenant_id, name="acme"),
            MetaPrOnboardRequest(html_url="https://github.com/other/meta/pull/1"),
        )
    assert exc_info.value.details.get("reason") == "meta_pr_wrong_repo"


@pytest.mark.asyncio
async def test_onboard_rejects_non_init() -> None:
    tenant_id = uuid4()
    pulls = [
        GithubPullRequestDocument(
            number=2,
            html_url="https://github.com/acme/prayog-meta/pull/2",
            title="chore: docs",
            state="open",
        )
    ]
    service, _, _, _ = _service(programme=_programme(tenant_id), pulls=pulls, runs=[])
    with pytest.raises(UnprocessableEntityError) as exc_info:
        await service.onboard_meta_pr(
            tenant_id,
            TenantResolvedContext(tenant_id=tenant_id, name="acme"),
            MetaPrOnboardRequest(html_url="https://github.com/acme/prayog-meta/pull/2"),
        )
    assert exc_info.value.details.get("reason") == "not_init_meta_pr"


@pytest.mark.asyncio
async def test_list_marks_onboarded_catalogue_row() -> None:
    tenant_id = uuid4()
    programme = _programme(tenant_id)
    pulls = [
        GithubPullRequestDocument(
            number=1,
            html_url="https://github.com/acme/prayog-meta/pull/1",
            title="INIT-ACME-001 intake",
            state="open",
        )
    ]
    service, _, _, _ = _service(programme=programme, pulls=pulls, runs=[])
    service._programme_meta_pr_repository.list_by_programme = AsyncMock(
        return_value=[
            ProgrammeMetaPrReadModel(
                id=uuid4(),
                programme_id=programme.id,
                html_url="https://github.com/acme/prayog-meta/pull/1",
                number=1,
                initiative_id="INIT-ACME-001",
                title="INIT-ACME-001 intake",
            )
        ]
    )
    result = await service.list_meta_prs(
        tenant_id,
        TenantResolvedContext(tenant_id=tenant_id, name="acme"),
    )
    assert result.items[0].onboarded is True


@pytest.mark.asyncio
async def test_list_onboarded_skips_github_list() -> None:
    tenant_id = uuid4()
    programme = _programme(tenant_id)
    service, _, forge, _ = _service(programme=programme, pulls=[], runs=[])
    service._programme_meta_pr_repository.list_by_programme = AsyncMock(
        return_value=[
            ProgrammeMetaPrReadModel(
                id=uuid4(),
                programme_id=programme.id,
                html_url="https://github.com/acme/prayog-meta/pull/1",
                number=1,
                initiative_id="INIT-ACME-001",
                title="INIT-ACME-001 intake",
            )
        ]
    )
    result = await service.list_onboarded_meta_prs(
        tenant_id,
        TenantResolvedContext(tenant_id=tenant_id, name="acme"),
    )
    assert len(result.items) == 1
    assert result.items[0].onboarded is True
    assert result.items[0].initiative_id == "INIT-ACME-001"
    forge.list_pull_requests.assert_not_called()
