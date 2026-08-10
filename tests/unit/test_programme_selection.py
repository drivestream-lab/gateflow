"""Unit tests for programme select/deselect/setup (INIT-GATEFLOW-013 W1/W2)."""

from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from src.business_services.programme_onboarding_service import ProgrammeOnboardingService
from src.exceptions.app_exceptions import UnprocessableEntityError
from src.infra_services.tenant_git_workspace_client import TenantGitWorkspaceError
from src.models.programme_catalogue_models import CatalogueCandidate
from src.models.programme_connection_models import ProgrammeConnectionReadModel
from src.models.programme_readiness_models import (
    LaunchpadStatusVerdict,
    LaunchpadStatusVerdictType,
)
from src.models.programme_selection_models import (
    ProgrammeDeselectRequest,
    ProgrammeRepoAdmitOutcomeType,
    ProgrammeSelectRequest,
)
from src.models.run_store_models import RunModel
from src.models.run_store_types import RunStatusType
from src.models.tenant_git_workspace_models import WorkspaceResolveModeType, WorkspaceResolveResult
from src.models.tenant_models import PatProbeResult, TenantRepoRef, TenantResolvedContext


@pytest.fixture
def tenant_id():
    return uuid4()


@pytest.fixture
def resolved(tenant_id):
    return TenantResolvedContext(tenant_id=tenant_id, name="acme")


def _connection(tenant_id):
    return ProgrammeConnectionReadModel(
        tenant_id=tenant_id,
        org="drivestream-lab",
        repo="prayog-meta",
        ref=None,
        last_synced_at=datetime.now(UTC),
    )


def _service(
    *,
    tenant_id,
    active: list[TenantRepoRef] | None = None,
    probe_results: list[PatProbeResult] | None = None,
    active_run: RunModel | None = None,
    resolve_side_effect=None,
):
    postgres = MagicMock()
    session = MagicMock()

    class _Tx:
        async def __aenter__(self):
            return session

        async def __aexit__(self, *args):
            return None

    postgres.transaction = MagicMock(return_value=_Tx())

    repo = MagicMock()
    repo.get_programme_connection = AsyncMock(return_value=_connection(tenant_id))
    repo.get_tenant_workspace_auth = AsyncMock(return_value=("/tmp/ws", "ghp_x"))
    active_list = list(active or [])
    repo.list_tenant_repos = AsyncMock(side_effect=lambda *_a, **_k: list(active_list))

    async def _add(_session, *, tenant_id, repos, readiness_source=None):  # noqa: ARG001
        active_list.extend(repos)

    async def _remove(_session, *, tenant_id, org, repo):  # noqa: ARG001
        before = len(active_list)
        active_list[:] = [r for r in active_list if not (r.org == org and r.repo == repo)]
        return len(active_list) < before

    repo.add_tenant_repos = AsyncMock(side_effect=_add)
    repo.remove_tenant_repo = AsyncMock(side_effect=_remove)
    repo.set_harness_verified = AsyncMock()
    repo.get_readiness_source = AsyncMock(return_value=None)

    probe = MagicMock()
    results = probe_results or [PatProbeResult(ok=True)]
    probe.verify_read_access = AsyncMock(side_effect=results)

    run_repo = MagicMock()
    run_repo.find_active_run = AsyncMock(return_value=active_run)

    git = MagicMock()
    if resolve_side_effect is None:
        git.resolve_workspace = AsyncMock(
            return_value=WorkspaceResolveResult(
                path="/tmp/ws/org/repo",
                mode=WorkspaceResolveModeType.CLONED,
            )
        )
    else:
        git.resolve_workspace = AsyncMock(side_effect=resolve_side_effect)

    status = MagicMock()
    status.inspect_status = AsyncMock(
        return_value=LaunchpadStatusVerdict(
            verdict_type=LaunchpadStatusVerdictType.READY,
            ready=True,
        )
    )
    svc = ProgrammeOnboardingService(
        postgres_service=postgres,
        tenant_repository=repo,
        tenant_git_workspace_client=git,
        github_pat_probe=probe,
        run_repository=run_repo,
        launchpad_status_client=status,
    )
    return svc, repo, probe, run_repo, active_list, git, status


def _candidates() -> list[CatalogueCandidate]:
    return [
        CatalogueCandidate(
            org="drivestream-lab",
            repo="gateflow",
            service_key="gateflow",
            status="active",
        ),
        CatalogueCandidate(
            org="drivestream-lab",
            repo="other",
            service_key="other",
            status="active",
        ),
    ]


@pytest.mark.asyncio
async def test_select_admits_in_catalogue(tenant_id, resolved) -> None:
    svc, repo, probe, _, active, git, status = _service(tenant_id=tenant_id)
    with patch(
        "src.business_services.programme_onboarding_service.parse_candidates",
        return_value=_candidates(),
    ):
        result = await svc.select_repos(
            tenant_id,
            ProgrammeSelectRequest(repos=[TenantRepoRef(org="drivestream-lab", repo="gateflow")]),
            resolved=resolved,
        )
    assert any(r.outcome == ProgrammeRepoAdmitOutcomeType.OK for r in result.results)
    assert TenantRepoRef(org="drivestream-lab", repo="gateflow") in result.active_repos
    repo.add_tenant_repos.assert_awaited_once()
    probe.verify_read_access.assert_awaited_once()
    git.resolve_workspace.assert_awaited_once()
    status.inspect_status.assert_awaited_once()
    assert len(active) == 1


@pytest.mark.asyncio
async def test_select_rejects_out_of_catalogue_zero_change(tenant_id, resolved) -> None:
    svc, repo, probe, _, active, git, status = _service(tenant_id=tenant_id)
    with patch(
        "src.business_services.programme_onboarding_service.parse_candidates",
        return_value=_candidates(),
    ):
        with pytest.raises(UnprocessableEntityError) as exc_info:
            await svc.select_repos(
                tenant_id,
                ProgrammeSelectRequest(repos=[TenantRepoRef(org="evil", repo="nope")]),
                resolved=resolved,
            )
    assert exc_info.value.details["reason"] == "out_of_catalogue"
    repo.add_tenant_repos.assert_not_called()
    probe.verify_read_access.assert_not_called()
    git.resolve_workspace.assert_not_called()
    status.inspect_status.assert_not_called()
    assert active == []


@pytest.mark.asyncio
async def test_select_probe_failure_zero_change(tenant_id, resolved) -> None:
    svc, repo, _, _, active, git, status = _service(
        tenant_id=tenant_id,
        probe_results=[PatProbeResult(ok=False, reason="not_found")],
    )
    with patch(
        "src.business_services.programme_onboarding_service.parse_candidates",
        return_value=_candidates(),
    ):
        with pytest.raises(UnprocessableEntityError) as exc_info:
            await svc.select_repos(
                tenant_id,
                ProgrammeSelectRequest(
                    repos=[TenantRepoRef(org="drivestream-lab", repo="gateflow")]
                ),
                resolved=resolved,
            )
    assert exc_info.value.details["reason"] == "probe_failed"
    repo.add_tenant_repos.assert_not_called()
    git.resolve_workspace.assert_not_called()
    status.inspect_status.assert_not_called()
    assert active == []


@pytest.mark.asyncio
async def test_select_already_selected_skips_probe(tenant_id, resolved) -> None:
    existing = [TenantRepoRef(org="drivestream-lab", repo="gateflow")]
    svc, repo, probe, _, _, git, status = _service(tenant_id=tenant_id, active=existing)
    with patch(
        "src.business_services.programme_onboarding_service.parse_candidates",
        return_value=_candidates(),
    ):
        result = await svc.select_repos(
            tenant_id,
            ProgrammeSelectRequest(repos=existing),
            resolved=resolved,
        )
    assert result.results[0].outcome == ProgrammeRepoAdmitOutcomeType.ALREADY_SELECTED
    repo.add_tenant_repos.assert_not_called()
    probe.verify_read_access.assert_not_called()
    git.resolve_workspace.assert_not_called()
    status.inspect_status.assert_not_called()


@pytest.mark.asyncio
async def test_select_setup_isolation_mixed_batch(tenant_id, resolved) -> None:
    """REQ-15/16: one setup failure does not block peers; membership kept."""

    async def _resolve(credential, *, ref=None):  # noqa: ARG001
        if credential.repo == "other":
            raise TenantGitWorkspaceError(
                "clone failed",
                reason="clone_failed:auth",
                org=credential.org,
                repo=credential.repo,
            )
        return WorkspaceResolveResult(
            path=f"/tmp/ws/{credential.org}/{credential.repo}",
            mode=WorkspaceResolveModeType.CLONED,
        )

    svc, repo, _, _, active, git, status = _service(
        tenant_id=tenant_id,
        probe_results=[PatProbeResult(ok=True), PatProbeResult(ok=True)],
        resolve_side_effect=_resolve,
    )
    with patch(
        "src.business_services.programme_onboarding_service.parse_candidates",
        return_value=_candidates(),
    ):
        result = await svc.select_repos(
            tenant_id,
            ProgrammeSelectRequest(
                repos=[
                    TenantRepoRef(org="drivestream-lab", repo="gateflow"),
                    TenantRepoRef(org="drivestream-lab", repo="other"),
                ]
            ),
            resolved=resolved,
        )

    by_repo = {r.repo: r for r in result.results}
    assert by_repo["gateflow"].outcome == ProgrammeRepoAdmitOutcomeType.OK
    assert by_repo["other"].outcome == ProgrammeRepoAdmitOutcomeType.SETUP_FAILED
    assert by_repo["other"].reason == "clone_failed:auth"
    assert TenantRepoRef(org="drivestream-lab", repo="gateflow") in result.active_repos
    assert TenantRepoRef(org="drivestream-lab", repo="other") in result.active_repos
    assert len(active) == 2
    assert git.resolve_workspace.await_count == 2
    assert status.inspect_status.await_count == 1
    repo.add_tenant_repos.assert_awaited_once()


@pytest.mark.asyncio
async def test_deselect_removes_membership(tenant_id, resolved) -> None:
    existing = [TenantRepoRef(org="drivestream-lab", repo="gateflow")]
    svc, repo, _, run_repo, active, _, _ = _service(tenant_id=tenant_id, active=existing)
    result = await svc.deselect_repo(
        tenant_id,
        ProgrammeDeselectRequest(org="drivestream-lab", repo="gateflow"),
        resolved=resolved,
    )
    assert result.active_repos == []
    assert active == []
    repo.remove_tenant_repo.assert_awaited_once()
    run_repo.find_active_run.assert_awaited_once()


@pytest.mark.asyncio
async def test_deselect_blocked_by_active_run(tenant_id, resolved) -> None:
    existing = [TenantRepoRef(org="drivestream-lab", repo="gateflow")]
    run = RunModel(
        id=uuid4(),
        org="drivestream-lab",
        repo="gateflow",
        status_type=RunStatusType.ACTIVE,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    svc, repo, _, _, active, _, _ = _service(tenant_id=tenant_id, active=existing, active_run=run)
    with pytest.raises(UnprocessableEntityError) as exc_info:
        await svc.deselect_repo(
            tenant_id,
            ProgrammeDeselectRequest(org="drivestream-lab", repo="gateflow"),
            resolved=resolved,
        )
    assert exc_info.value.details["reason"] == "active_run"
    repo.remove_tenant_repo.assert_not_called()
    assert active == existing
