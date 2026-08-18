"""Unit tests for LaunchpadApplyHarnessClient (Launchpad >= 0.5.35)."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.infra_services.launchpad_apply_harness_client import (
    LaunchpadApplyHarnessClient,
    LaunchpadApplyHarnessError,
)


def _apply_json(*, ok: bool, checks: list[dict[str, object]], error: str | None = None) -> str:
    return json.dumps(
        {
            "ok": ok,
            "command": "apply-harness",
            "repo": "example-api",
            "exit": 0 if ok else 1,
            "error": error,
            "checks": checks,
        }
    )


@pytest.fixture
def client() -> LaunchpadApplyHarnessClient:
    settings = MagicMock()
    settings.launchpad_cli_path = "launchpad"
    with patch(
        "src.infra_services.launchpad_apply_harness_client.AppSettings.get_instance",
        return_value=settings,
    ):
        c = LaunchpadApplyHarnessClient()
    c._settings = settings
    c._initialized = True
    return c


def test_build_apply_argv_service_mode(client: LaunchpadApplyHarnessClient) -> None:
    argv = client.build_apply_argv(
        meta_config_dir="/ws/meta/config",
        workspace="/ws/org",
        repo="gateflow",
    )
    assert argv == [
        "launchpad",
        "apply-harness",
        "--no-client",
        "--config-dir",
        "/ws/meta/config",
        "--workspace",
        "/ws/org",
        "--repo",
        "gateflow",
        "--apply",
        "--format",
        "json",
    ]
    assert "--token" not in argv
    assert "--client" not in argv


def test_apply_argv_requires_apply_flag(client: LaunchpadApplyHarnessClient) -> None:
    with pytest.raises(LaunchpadApplyHarnessError) as exc_info:
        client._assert_apply_argv(["launchpad", "apply-harness", "--no-client"])
    assert exc_info.value.reason == "argv_guard"


@pytest.mark.asyncio
async def test_apply_harness_ok(client: LaunchpadApplyHarnessClient, tmp_path: Path) -> None:
    repo_ws = tmp_path / "org" / "gateflow"
    meta = tmp_path / "org" / "prayog-meta"
    config = meta / "config"
    repo_ws.mkdir(parents=True)
    config.mkdir(parents=True)
    payload = _apply_json(
        ok=True,
        checks=[
            {"id": "clone", "ok": True, "detail": str(repo_ws)},
            {"id": "apply", "ok": True, "detail": "profile: python-backend"},
        ],
    )
    with patch(
        "src.infra_services.launchpad_apply_harness_client.run_launchpad_cli",
        new=AsyncMock(return_value=(0, payload, "")),
    ) as run:
        with patch(
            "src.infra_services.launchpad_apply_harness_client.launchpad_binary_available",
            return_value=True,
        ):
            verdict = await client.apply_harness(
                repo_workspace=str(repo_ws),
                meta_config_dir=str(meta),
                org="drivestream-lab",
                repo="gateflow",
                pat="ghp_programme_pat",
            )
    assert verdict.ok is True
    assert run.await_args is not None
    argv = run.await_args.args[0]
    assert "--apply" in argv
    assert argv[argv.index("--format") + 1] == "json"
    assert argv[argv.index("--config-dir") + 1] == str(config.resolve())
    assert run.await_args.kwargs["github_token"] == "ghp_programme_pat"


@pytest.mark.asyncio
async def test_apply_harness_not_ok_named_reason(
    client: LaunchpadApplyHarnessClient, tmp_path: Path
) -> None:
    repo_ws = tmp_path / "repo"
    meta = tmp_path / "meta"
    repo_ws.mkdir()
    meta.mkdir()
    payload = _apply_json(
        ok=False,
        checks=[{"id": "clone", "ok": False, "detail": "missing"}],
        error="local clone not found",
    )
    with patch(
        "src.infra_services.launchpad_apply_harness_client.run_launchpad_cli",
        new=AsyncMock(return_value=(1, payload, "")),
    ):
        with patch(
            "src.infra_services.launchpad_apply_harness_client.launchpad_binary_available",
            return_value=True,
        ):
            verdict = await client.apply_harness(
                repo_workspace=str(repo_ws),
                meta_config_dir=str(meta),
                org="o",
                repo="r",
                pat="ghp_test",
            )
    assert verdict.ok is False
    assert verdict.reason == "apply_failed:clone"


@pytest.mark.asyncio
async def test_apply_harness_tool_unavailable(
    client: LaunchpadApplyHarnessClient, tmp_path: Path
) -> None:
    with patch(
        "src.infra_services.launchpad_apply_harness_client.launchpad_binary_available",
        return_value=False,
    ):
        with pytest.raises(LaunchpadApplyHarnessError) as exc_info:
            await client.apply_harness(
                repo_workspace=str(tmp_path),
                meta_config_dir=str(tmp_path),
                org="o",
                repo="r",
                pat="ghp_test",
            )
    assert exc_info.value.reason == "tool_unavailable"
