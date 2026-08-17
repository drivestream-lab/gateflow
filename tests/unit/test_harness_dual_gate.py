"""Unit tests for dual harness readiness gates (INIT-GATEFLOW-013 W3)."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.business_services.wave_start_service import WaveStartService
from tests._helpers.programme_forge import mock_forge_factory
from src.exceptions.app_exceptions import UnprocessableEntityError
from src.models.programme_connection_models import ProgrammeConnectionReadModel
from src.models.programme_readiness_models import (
    LaunchpadStatusVerdict,
    LaunchpadStatusVerdictType,
    ReadinessSourceType,
)
from src.models.tenant_git_workspace_models import TenantWorkspaceCredential


def _wave_start_service(
    *,
    readiness_source: ReadinessSourceType | None,
    harness_verified: bool = False,
):
    tenant = MagicMock()
    tenant.get_workspace_credential_for_repo = AsyncMock(
        return_value=TenantWorkspaceCredential(
            tenant_id=uuid4(),
            workspace_root="/tmp/ws",
            pat="ghp_x",
            org="drivestream-lab",
            repo="gateflow",
        )
    )
    tenant.get_readiness_source = AsyncMock(return_value=readiness_source)
    tenant.is_harness_verified = AsyncMock(return_value=harness_verified)
    tenant.mark_harness_verified = AsyncMock()
    tenant.get_programme_connection = AsyncMock(
        return_value=ProgrammeConnectionReadModel(
            tenant_id=uuid4(),
            org="drivestream-lab",
            repo="prayog-meta",
            ref=None,
            last_synced_at=datetime.now(UTC),
        )
    )

    fs = MagicMock()
    fs.sync_harness = AsyncMock()
    status = MagicMock()
    status.inspect_status = AsyncMock(
        return_value=LaunchpadStatusVerdict(
            verdict_type=LaunchpadStatusVerdictType.READY,
            ready=True,
        )
    )

    svc = WaveStartService(
        postgres_service=MagicMock(),
        slot_validator=MagicMock(),
        workflow_engine=MagicMock(),
        metrics_emitter=MagicMock(),
        run_repository=MagicMock(),
        job_repository=MagicMock(),
        meta_pr_intake=MagicMock(),
        forge_client_factory=mock_forge_factory()[0],
        board_service=MagicMock(),
        tenant_service=tenant,
        tenant_git_workspace_client=MagicMock(),
        launchpad_client=fs,
        launchpad_status_client=status,
        programme_repository=MagicMock(),
        programme_meta_pr_repository=MagicMock(),
        checkpoint_evidence_service=MagicMock(),
    )
    return svc, tenant, fs, status


@pytest.mark.asyncio
async def test_status_sourced_cache_hit_skips_both_evaluators() -> None:
    svc, _, fs, status = _wave_start_service(
        readiness_source=ReadinessSourceType.LAUNCHPAD_STATUS,
        harness_verified=True,
    )
    await svc._ensure_implement_harness_ready(
        org="drivestream-lab",
        repo="gateflow",
        workspace_path="/tmp/ws/drivestream-lab/gateflow",
        force=False,
    )
    fs.sync_harness.assert_not_called()
    status.inspect_status.assert_not_called()


@pytest.mark.asyncio
async def test_status_sourced_never_checked_fail_closed() -> None:
    svc, _, fs, status = _wave_start_service(
        readiness_source=ReadinessSourceType.LAUNCHPAD_STATUS,
        harness_verified=False,
    )
    with pytest.raises(UnprocessableEntityError) as exc_info:
        await svc._ensure_implement_harness_ready(
            org="drivestream-lab",
            repo="gateflow",
            workspace_path="/tmp/ws/drivestream-lab/gateflow",
            force=False,
        )
    assert exc_info.value.details["reason"] == "never_checked"
    fs.sync_harness.assert_not_called()
    status.inspect_status.assert_not_called()


@pytest.mark.asyncio
async def test_filesystem_force_recheck_never_calls_status() -> None:
    svc, _, fs, status = _wave_start_service(
        readiness_source=None,
        harness_verified=True,
    )
    await svc._ensure_implement_harness_ready(
        org="drivestream-lab",
        repo="gateflow",
        workspace_path="/tmp/ws/drivestream-lab/gateflow",
        force=True,
    )
    fs.sync_harness.assert_awaited_once()
    status.inspect_status.assert_not_called()


@pytest.mark.asyncio
async def test_status_force_recheck_calls_status_not_filesystem() -> None:
    svc, tenant, fs, status = _wave_start_service(
        readiness_source=ReadinessSourceType.LAUNCHPAD_STATUS,
        harness_verified=False,
    )
    await svc._ensure_implement_harness_ready(
        org="drivestream-lab",
        repo="gateflow",
        workspace_path="/tmp/ws/drivestream-lab/gateflow",
        force=True,
    )
    status.inspect_status.assert_awaited_once()
    fs.sync_harness.assert_not_called()
    tenant.mark_harness_verified.assert_awaited()
