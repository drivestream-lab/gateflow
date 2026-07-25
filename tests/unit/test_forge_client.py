"""Unit tests for ForgeClient forbidden operations and PR-at-start (FR-19)."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.infra_services.forge_client import ForgeClient


def _forge_client() -> ForgeClient:
    token_provider = AsyncMock()
    token_provider.get_token = AsyncMock(return_value="test-token")
    return ForgeClient(token_provider=token_provider)


@pytest.mark.asyncio
async def test_forge_client_forbids_gate_labels() -> None:
    client = _forge_client()
    with pytest.raises(PermissionError, match="forbids gate-approval"):
        client.add_labels(["spec-lgtm"])


@pytest.mark.asyncio
async def test_forge_client_forbids_auto_merge() -> None:
    client = _forge_client()
    with pytest.raises(PermissionError, match="auto-merge"):
        client.enable_auto_merge()


@pytest.mark.asyncio
async def test_create_or_update_pull_request_creates_when_absent() -> None:
    client = _forge_client()
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
    client = _forge_client()
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


@pytest.mark.asyncio
async def test_forge_client_initialize_sets_bearer() -> None:
    token_provider = AsyncMock()
    token_provider.get_token = AsyncMock(return_value="ghp_from_provider")
    client = ForgeClient(token_provider=token_provider)
    await client.initialize()
    assert client._client is not None
    assert client._client.headers["Authorization"] == "Bearer ghp_from_provider"
    await client.close()


@pytest.mark.asyncio
async def test_ensure_branch_from_base_creates_when_missing() -> None:
    client = _forge_client()
    http = MagicMock()
    base_ref = MagicMock()
    base_ref.raise_for_status = MagicMock()
    base_ref.json.return_value = {"object": {"sha": "base-sha"}}
    missing = MagicMock()
    missing.status_code = 404
    created_ref_resp = MagicMock()
    created_ref_resp.raise_for_status = MagicMock()
    created_ref_resp.json.return_value = {"object": {"sha": "base-sha"}}
    parent = MagicMock()
    parent.raise_for_status = MagicMock()
    parent.json.return_value = {"tree": {"sha": "tree-sha"}}
    commit = MagicMock()
    commit.raise_for_status = MagicMock()
    commit.json.return_value = {"sha": "new-sha"}
    patched = MagicMock()
    patched.raise_for_status = MagicMock()
    http.get = AsyncMock(side_effect=[base_ref, missing, parent])
    http.post = AsyncMock(side_effect=[created_ref_resp, commit])
    http.patch = AsyncMock(return_value=patched)
    client._client = http
    client._initialized = True

    created_new = await client.ensure_branch_from_base(
        "acme", "widget", branch="gateflow/run-deadbeef", base="develop"
    )
    assert created_new is True
    assert http.post.await_count == 2
    http.patch.assert_awaited()


@pytest.mark.asyncio
async def test_ensure_branch_from_base_noop_when_present() -> None:
    client = _forge_client()
    http = MagicMock()
    base_ref = MagicMock()
    base_ref.raise_for_status = MagicMock()
    base_ref.json.return_value = {"object": {"sha": "base-sha"}}
    present = MagicMock()
    present.status_code = 200
    present.json.return_value = {"object": {"sha": "other-sha"}}
    http.get = AsyncMock(side_effect=[base_ref, present])
    client._client = http
    client._initialized = True

    created_new = await client.ensure_branch_from_base(
        "acme", "widget", branch="gateflow/run-deadbeef", base="develop"
    )
    assert created_new is False
    http.post.assert_not_called()
