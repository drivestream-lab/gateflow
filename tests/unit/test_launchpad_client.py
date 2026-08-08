"""Unit tests for LaunchpadClient harness readiness (INIT-GATEFLOW-012 W3 / FF-05)."""

from pathlib import Path

import pytest

from src.infra_services.launchpad_client import HarnessReadinessError, LaunchpadClient


def _ready_workspace(root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    (root / ".harness-pin.yaml").write_text("profile: python-backend\n", encoding="utf-8")
    (root / ".harness").mkdir()
    return root


@pytest.mark.asyncio
async def test_sync_harness_ready_passes(tmp_path: Path) -> None:
    client = LaunchpadClient()
    await client.initialize()
    ws = _ready_workspace(tmp_path / "ready")
    await client.sync_harness(str(ws))


@pytest.mark.asyncio
async def test_sync_harness_missing_path_raises(tmp_path: Path) -> None:
    client = LaunchpadClient()
    await client.initialize()
    missing = tmp_path / "no-such-dir"
    with pytest.raises(FileNotFoundError, match="Workspace path not found"):
        await client.sync_harness(str(missing))


@pytest.mark.asyncio
async def test_sync_harness_missing_pin_named_fail(tmp_path: Path) -> None:
    client = LaunchpadClient()
    await client.initialize()
    ws = tmp_path / "no-pin"
    ws.mkdir()
    (ws / ".harness").mkdir()
    with pytest.raises(HarnessReadinessError) as exc_info:
        await client.sync_harness(str(ws))
    err = exc_info.value
    assert err.reason == "harness_artifacts_missing"
    assert ".harness-pin.yaml" in err.missing
    assert ".harness" not in err.missing


@pytest.mark.asyncio
async def test_sync_harness_missing_dir_named_fail(tmp_path: Path) -> None:
    client = LaunchpadClient()
    await client.initialize()
    ws = tmp_path / "no-harness-dir"
    ws.mkdir()
    (ws / ".harness-pin.yaml").write_text("profile: python-backend\n", encoding="utf-8")
    with pytest.raises(HarnessReadinessError) as exc_info:
        await client.sync_harness(str(ws))
    err = exc_info.value
    assert err.reason == "harness_artifacts_missing"
    assert ".harness" in err.missing


@pytest.mark.asyncio
async def test_sync_harness_missing_both(tmp_path: Path) -> None:
    client = LaunchpadClient()
    await client.initialize()
    ws = tmp_path / "empty"
    ws.mkdir()
    with pytest.raises(HarnessReadinessError) as exc_info:
        await client.sync_harness(str(ws))
    err = exc_info.value
    assert err.reason == "harness_artifacts_missing"
    assert ".harness-pin.yaml" in err.missing
    assert ".harness" in err.missing
