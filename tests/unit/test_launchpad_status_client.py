"""Unit tests for LaunchpadStatusClient (INIT-GATEFLOW-013 W3 / Launchpad 0.5.35 JSON)."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.infra_services.launchpad_status_client import (
    LaunchpadStatusClient,
    LaunchpadStatusError,
)
from src.models.programme_readiness_models import LaunchpadStatusVerdictType


def _status_json(*, ok: bool, checks: list[dict[str, object]]) -> str:
    return json.dumps(
        {
            "ok": ok,
            "command": "status",
            "repo": "r",
            "exit": 0 if ok else 1,
            "error": None,
            "checks": checks,
        }
    )


@pytest.fixture
def client() -> LaunchpadStatusClient:
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


def test_build_status_argv_service_mode(client: LaunchpadStatusClient) -> None:
    argv = client.build_status_argv(
        meta_config_dir="/ws/meta/config",
        workspace="/ws/org",
        repo="gateflow-ops",
    )
    assert argv == [
        "launchpad",
        "status",
        "--no-client",
        "--config-dir",
        "/ws/meta/config",
        "--workspace",
        "/ws/org",
        "--repo",
        "gateflow-ops",
        "--format",
        "json",
    ]
    assert "--meta" not in argv
    assert "apply" not in argv


@pytest.mark.asyncio
async def test_inspect_status_argv_and_child_token(
    client: LaunchpadStatusClient, tmp_path: Path
) -> None:
    repo_ws = tmp_path / "org" / "gateflow-ops"
    meta = tmp_path / "org" / "prayog-meta"
    config = meta / "config"
    repo_ws.mkdir(parents=True)
    config.mkdir(parents=True)
    payload = _status_json(ok=True, checks=[{"id": "clone", "ok": True, "detail": ""}])
    with patch(
        "src.infra_services.launchpad_status_client.run_launchpad_cli",
        new=AsyncMock(return_value=(0, payload, "")),
    ) as run:
        with patch(
            "src.infra_services.launchpad_status_client.launchpad_binary_available",
            return_value=True,
        ):
            await client.inspect_status(
                repo_workspace=str(repo_ws),
                meta_config_dir=str(meta),
                org="drivestream-lab",
                repo="gateflow-ops",
                pat="ghp_programme_pat",
            )
    assert run.await_args is not None
    argv = run.await_args.args[0]
    assert "--no-client" in argv
    assert "--format" in argv
    assert argv[argv.index("--format") + 1] == "json"
    assert "--meta" not in argv
    assert argv[argv.index("--config-dir") + 1] == str(config.resolve())
    assert argv[argv.index("--workspace") + 1] == str(repo_ws.parent.resolve())
    assert argv[argv.index("--repo") + 1] == "gateflow-ops"
    assert run.await_args.kwargs["github_token"] == "ghp_programme_pat"


def test_argv_guard_rejects_apply(client: LaunchpadStatusClient) -> None:
    with pytest.raises(LaunchpadStatusError) as exc_info:
        client._assert_inspect_only(["launchpad", "apply", "--config-dir", "/x"])
    assert exc_info.value.reason == "argv_guard"


@pytest.mark.asyncio
async def test_inspect_status_tool_unavailable(
    client: LaunchpadStatusClient, tmp_path: Path
) -> None:
    with patch(
        "src.infra_services.launchpad_status_client.launchpad_binary_available",
        return_value=False,
    ):
        with pytest.raises(LaunchpadStatusError) as exc_info:
            await client.inspect_status(
                repo_workspace=str(tmp_path),
                meta_config_dir=str(tmp_path),
                org="o",
                repo="r",
                pat="ghp_test",
            )
    assert exc_info.value.reason == "tool_unavailable"


@pytest.mark.asyncio
async def test_inspect_status_rejects_blank_pat(
    client: LaunchpadStatusClient, tmp_path: Path
) -> None:
    repo_ws = tmp_path / "repo"
    meta = tmp_path / "meta"
    repo_ws.mkdir()
    meta.mkdir()
    with patch(
        "src.infra_services.launchpad_status_client.launchpad_binary_available",
        return_value=True,
    ):
        with pytest.raises(LaunchpadStatusError) as exc_info:
            await client.inspect_status(
                repo_workspace=str(repo_ws),
                meta_config_dir=str(meta),
                org="o",
                repo="r",
                pat="   ",
            )
    assert exc_info.value.reason == "programme_pat_missing"


@pytest.mark.asyncio
async def test_inspect_status_ready(client: LaunchpadStatusClient, tmp_path: Path) -> None:
    repo_ws = tmp_path / "repo"
    meta = tmp_path / "meta"
    repo_ws.mkdir()
    meta.mkdir()
    payload = _status_json(
        ok=True,
        checks=[
            {"id": "governance", "ok": True, "detail": ""},
            {"id": "harness", "ok": True, "detail": "profile: python-backend"},
        ],
    )
    with patch(
        "src.infra_services.launchpad_status_client.run_launchpad_cli",
        new=AsyncMock(return_value=(0, payload, "")),
    ) as run:
        with patch(
            "src.infra_services.launchpad_status_client.launchpad_binary_available",
            return_value=True,
        ):
            verdict = await client.inspect_status(
                repo_workspace=str(repo_ws),
                meta_config_dir=str(meta),
                org="o",
                repo="r",
                pat="ghp_test",
            )
    assert verdict.ready is True
    assert verdict.verdict_type == LaunchpadStatusVerdictType.READY
    assert run.await_args is not None
    argv = run.await_args.args[0]
    assert "apply" not in argv
    assert "status" in argv
    assert "--format" in argv


@pytest.mark.asyncio
async def test_inspect_status_not_ready_uses_json_check_id(
    client: LaunchpadStatusClient, tmp_path: Path
) -> None:
    repo_ws = tmp_path / "repo"
    meta = tmp_path / "meta"
    repo_ws.mkdir()
    meta.mkdir()
    payload = _status_json(
        ok=False,
        checks=[
            {"id": "governance", "ok": True, "detail": ""},
            {"id": "board", "ok": False, "detail": "not configured"},
            {"id": "harness", "ok": False, "detail": "not applied"},
            {"id": "forge", "ok": False, "detail": "stale"},
        ],
    )
    with patch(
        "src.infra_services.launchpad_status_client.run_launchpad_cli",
        new=AsyncMock(return_value=(1, payload, "")),
    ):
        with patch(
            "src.infra_services.launchpad_status_client.launchpad_binary_available",
            return_value=True,
        ):
            verdict = await client.inspect_status(
                repo_workspace=str(repo_ws),
                meta_config_dir=str(meta),
                org="o",
                repo="r",
                pat="ghp_test",
            )
    assert verdict.ready is False
    assert verdict.reason == "repo_not_ready:harness"


@pytest.mark.asyncio
async def test_inspect_status_ready_when_only_advisory_board_and_forge_fail(
    client: LaunchpadStatusClient, tmp_path: Path
) -> None:
    """Admit must succeed when clone/harness are ok; Gateflow does not apply forge templates."""
    repo_ws = tmp_path / "repo"
    meta = tmp_path / "meta"
    repo_ws.mkdir()
    meta.mkdir()
    payload = _status_json(
        ok=False,
        checks=[
            {"id": "governance", "ok": True, "detail": "stack: python-backend"},
            {"id": "board", "ok": False, "detail": "not configured"},
            {"id": "clone", "ok": True, "detail": str(repo_ws)},
            {"id": "scaffold", "ok": True, "detail": "applied"},
            {"id": "harness", "ok": True, "detail": "profile: python-backend"},
            {"id": "forge", "ok": False, "detail": "stale"},
            {"id": "drift", "ok": True, "detail": "none"},
        ],
    )
    with patch(
        "src.infra_services.launchpad_status_client.run_launchpad_cli",
        new=AsyncMock(return_value=(1, payload, "")),
    ):
        with patch(
            "src.infra_services.launchpad_status_client.launchpad_binary_available",
            return_value=True,
        ):
            verdict = await client.inspect_status(
                repo_workspace=str(repo_ws),
                meta_config_dir=str(meta),
                org="o",
                repo="r",
                pat="ghp_test",
            )
    assert verdict.ready is True
    assert verdict.verdict_type == LaunchpadStatusVerdictType.READY
    assert verdict.reason is None


@pytest.mark.asyncio
async def test_inspect_status_invalid_json_is_tool_failure(
    client: LaunchpadStatusClient, tmp_path: Path
) -> None:
    repo_ws = tmp_path / "repo"
    meta = tmp_path / "meta"
    repo_ws.mkdir()
    meta.mkdir()
    with patch(
        "src.infra_services.launchpad_status_client.run_launchpad_cli",
        new=AsyncMock(return_value=(1, "not json", "")),
    ):
        with patch(
            "src.infra_services.launchpad_status_client.launchpad_binary_available",
            return_value=True,
        ):
            with pytest.raises(LaunchpadStatusError) as exc_info:
                await client.inspect_status(
                    repo_workspace=str(repo_ws),
                    meta_config_dir=str(meta),
                    org="o",
                    repo="r",
                    pat="ghp_test",
                )
    assert exc_info.value.reason == "json_parse_failed"
