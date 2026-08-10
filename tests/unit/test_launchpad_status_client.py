"""Unit tests for LaunchpadStatusClient (INIT-GATEFLOW-013 W3)."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.infra_services.launchpad_status_client import (
    LaunchpadStatusClient,
    LaunchpadStatusError,
)
from src.models.programme_readiness_models import LaunchpadStatusVerdictType


@pytest.fixture
def client(tmp_path: Path) -> LaunchpadStatusClient:
    settings = MagicMock()
    settings.launchpad_cli_path = "launchpad"
    with patch(
        "src.infra_services.launchpad_status_client.AppSettings.get_instance",
        return_value=settings,
    ):
        c = LaunchpadStatusClient()
    c._settings = settings
    c._initialized = True
    return c


def test_build_status_argv_inspect_only(client: LaunchpadStatusClient) -> None:
    argv = client.build_status_argv(
        repo_workspace="/ws/org/repo",
        meta_config_dir="/ws/meta/org",
        org="org",
        repo="repo",
    )
    assert argv[0] == "launchpad"
    assert "status" in argv
    assert "apply" not in argv
    assert "--config-dir" in argv
    assert "--meta" in argv


def test_argv_guard_rejects_apply(client: LaunchpadStatusClient) -> None:
    with pytest.raises(LaunchpadStatusError) as exc_info:
        client._assert_inspect_only(["launchpad", "apply", "--config-dir", "/x"])
    assert exc_info.value.reason == "argv_guard"


@pytest.mark.asyncio
async def test_inspect_status_tool_unavailable(
    client: LaunchpadStatusClient, tmp_path: Path
) -> None:
    client._binary_available = MagicMock(return_value=False)  # type: ignore[method-assign]
    with pytest.raises(LaunchpadStatusError) as exc_info:
        await client.inspect_status(
            repo_workspace=str(tmp_path),
            meta_config_dir=str(tmp_path),
            org="o",
            repo="r",
        )
    assert exc_info.value.reason == "tool_unavailable"


@pytest.mark.asyncio
async def test_inspect_status_ready(client: LaunchpadStatusClient, tmp_path: Path) -> None:
    repo_ws = tmp_path / "repo"
    meta = tmp_path / "meta"
    repo_ws.mkdir()
    meta.mkdir()
    client._binary_available = MagicMock(return_value=True)  # type: ignore[method-assign]
    client._run = AsyncMock(return_value=(0, ""))  # type: ignore[method-assign]
    verdict = await client.inspect_status(
        repo_workspace=str(repo_ws),
        meta_config_dir=str(meta),
        org="o",
        repo="r",
    )
    assert verdict.ready is True
    assert verdict.verdict_type == LaunchpadStatusVerdictType.READY
    assert client._run.await_args is not None
    argv = client._run.await_args.args[0]
    assert "apply" not in argv
    assert "status" in argv
