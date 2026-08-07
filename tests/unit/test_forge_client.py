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


@pytest.mark.asyncio
async def test_get_branch_tip_sha() -> None:
    client = _forge_client()
    http = MagicMock()
    ref = MagicMock()
    ref.raise_for_status = MagicMock()
    ref.json.return_value = {"object": {"sha": "tipsha0"}}
    http.get = AsyncMock(return_value=ref)
    client._client = http

    sha = await client.get_branch_tip_sha("acme", "widget", branch="feature/x")
    assert sha == "tipsha0"
    http.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_commit_paths_to_branch_creates_blobs_tree_commit(tmp_path) -> None:
    from pathlib import Path

    workspace = Path(tmp_path)
    (workspace / "docs").mkdir()
    (workspace / "docs" / "a.md").write_text("hello\n", encoding="utf-8")

    client = _forge_client()
    http = MagicMock()

    ref = MagicMock()
    ref.raise_for_status = MagicMock()
    ref.json.return_value = {"object": {"sha": "headsha"}}

    parent = MagicMock()
    parent.raise_for_status = MagicMock()
    parent.json.return_value = {"tree": {"sha": "treesha"}}

    blob = MagicMock()
    blob.raise_for_status = MagicMock()
    blob.json.return_value = {"sha": "blobsha"}

    tree = MagicMock()
    tree.raise_for_status = MagicMock()
    tree.json.return_value = {"sha": "newtree"}

    commit = MagicMock()
    commit.raise_for_status = MagicMock()
    commit.json.return_value = {"sha": "newcommit"}

    patched = MagicMock()
    patched.raise_for_status = MagicMock()

    http.get = AsyncMock(side_effect=[ref, parent])
    http.post = AsyncMock(side_effect=[blob, tree, commit])
    http.patch = AsyncMock(return_value=patched)
    client._client = http
    client._initialized = True

    result = await client.commit_paths_to_branch(
        "acme",
        "widget",
        branch="feature/wave",
        workspace_path=workspace,
        paths=["docs/a.md"],
        message="chore: publish",
    )
    assert result.commit_sha == "newcommit"
    assert result.path_count == 1
    assert result.paths == ["docs/a.md"]
    assert http.post.await_count == 3
    http.patch.assert_awaited()


@pytest.mark.asyncio
async def test_commit_paths_to_branch_empty_fails() -> None:
    client = _forge_client()
    client._client = MagicMock()
    client._initialized = True
    with pytest.raises(ValueError, match="at least one path"):
        await client.commit_paths_to_branch(
            "acme",
            "widget",
            branch="feature/wave",
            workspace_path=".",
            paths=[],
            message="x",
        )


@pytest.mark.asyncio
async def test_open_draft_pr_applies_projection_labels() -> None:
    client = _forge_client()
    http = MagicMock()
    listed = MagicMock()
    listed.raise_for_status = MagicMock()
    listed.json.return_value = []
    created = MagicMock()
    created.raise_for_status = MagicMock()
    created.json.return_value = {"number": 42}
    labeled = MagicMock()
    labeled.raise_for_status = MagicMock()
    http.get = AsyncMock(return_value=listed)
    http.post = AsyncMock(side_effect=[created, labeled])
    client._client = http
    client._initialized = True

    pr = await client.open_draft_pr(
        "acme",
        "widget",
        title="t",
        body="b",
        head="feature/x",
        base="develop",
        draft=True,
        apply_labels=["impact-map-pending"],
    )
    assert pr == 42
    assert http.post.await_count == 2
    create_json = http.post.await_args_list[0].kwargs["json"]
    assert create_json["draft"] is True


@pytest.mark.asyncio
async def test_open_draft_pr_forbids_lgtm_labels() -> None:
    client = _forge_client()
    client._client = MagicMock()
    client._initialized = True
    with pytest.raises(PermissionError, match="lgtm"):
        await client.open_draft_pr(
            "acme",
            "widget",
            title="t",
            body="b",
            head="feature/x",
            base="develop",
            apply_labels=["spec-lgtm"],
        )


@pytest.mark.asyncio
async def test_get_pull_request_includes_merge_fields() -> None:
    client = _forge_client()
    http = MagicMock()
    resp = MagicMock()
    resp.raise_for_status = MagicMock()
    resp.json.return_value = {
        "title": "Spec",
        "state": "closed",
        "labels": [{"name": "spec-lgtm"}],
        "head": {"ref": "chore/x", "sha": "abc123"},
        "base": {"ref": "develop", "sha": "def456"},
        "merged": True,
        "merge_commit_sha": "merge789",
        "merged_at": "2026-08-07T01:00:00Z",
    }
    http.get = AsyncMock(return_value=resp)
    client._client = http
    client._initialized = True

    pr = await client.get_pull_request("acme", "widget", 159)
    assert pr.merged is True
    assert pr.merge_commit_sha == "merge789"
    assert pr.head.sha == "abc123"
    http.get.assert_awaited_once_with("/repos/acme/widget/pulls/159")


@pytest.mark.asyncio
async def test_list_reviews_validates_documents() -> None:
    client = _forge_client()
    http = MagicMock()
    resp = MagicMock()
    resp.raise_for_status = MagicMock()
    resp.json.return_value = [
        {
            "id": 1,
            "user": {"login": "pe"},
            "state": "APPROVED",
            "submitted_at": "2026-08-06T17:29:07Z",
            "commit_id": "c5047eaa",
        }
    ]
    http.get = AsyncMock(return_value=resp)
    client._client = http
    client._initialized = True

    reviews = await client.list_reviews("acme", "widget", 159)
    assert len(reviews) == 1
    assert reviews[0].state == "APPROVED"
    assert reviews[0].user.login == "pe"
    http.get.assert_awaited_once_with("/repos/acme/widget/pulls/159/reviews")


@pytest.mark.asyncio
async def test_list_check_runs_validates_documents() -> None:
    client = _forge_client()
    http = MagicMock()
    resp = MagicMock()
    resp.raise_for_status = MagicMock()
    resp.json.return_value = {
        "total_count": 1,
        "check_runs": [
            {
                "name": "ci",
                "status": "completed",
                "conclusion": "success",
                "head_sha": "abc123",
            }
        ],
    }
    http.get = AsyncMock(return_value=resp)
    client._client = http
    client._initialized = True

    runs = await client.list_check_runs("acme", "widget", "abc123")
    assert len(runs) == 1
    assert runs[0].name == "ci"
    assert runs[0].conclusion == "success"
    http.get.assert_awaited_once_with("/repos/acme/widget/commits/abc123/check-runs")
