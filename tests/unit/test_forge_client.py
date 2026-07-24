"""Unit tests for ForgeClient forbidden operations and PR-at-start (FR-19)."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.infra_services.forge_client import ForgeClient


@pytest.mark.asyncio
async def test_forge_client_forbids_gate_labels() -> None:
    client = ForgeClient()
    with pytest.raises(PermissionError, match="forbids gate-approval"):
        client.add_labels(["spec-lgtm"])


@pytest.mark.asyncio
async def test_forge_client_forbids_auto_merge() -> None:
    client = ForgeClient()
    with pytest.raises(PermissionError, match="auto-merge"):
        client.enable_auto_merge()


@pytest.mark.asyncio
async def test_create_or_update_pull_request_creates_when_absent() -> None:
    client = ForgeClient()
    http = MagicMock()
    listed = MagicMock()
    listed.raise_for_status = MagicMock()
    listed.json.return_value = []
    created = MagicMock()
    created.raise_for_status = MagicMock()
    created.json.return_value = {"number": 12}
    http.get = AsyncMock(return_value=listed)
    http.post = AsyncMock(return_value=created)
    client._client = http
    client._initialized = True

    pr_number = await client.create_or_update_pull_request(
        "acme",
        "widget",
        title="t",
        body="b",
        head="gateflow/run-abcd",
        base="develop",
    )
    assert pr_number == 12
    http.post.assert_awaited()


@pytest.mark.asyncio
async def test_create_or_update_pull_request_updates_when_present() -> None:
    client = ForgeClient()
    http = MagicMock()
    listed = MagicMock()
    listed.raise_for_status = MagicMock()
    listed.json.return_value = [{"number": 9}]
    patched = MagicMock()
    patched.raise_for_status = MagicMock()
    http.get = AsyncMock(return_value=listed)
    http.patch = AsyncMock(return_value=patched)
    client._client = http
    client._initialized = True

    pr_number = await client.create_or_update_pull_request(
        "acme",
        "widget",
        title="t2",
        body="b2",
        head="gateflow/run-abcd",
        base="develop",
    )
    assert pr_number == 9
    http.patch.assert_awaited()
    http.post.assert_not_called()
