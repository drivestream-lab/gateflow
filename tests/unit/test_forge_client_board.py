"""Unit tests for ForgeClient board ops and gh-free production path (FR-24/25/26a)."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.infra_services.forge_client import ForgeClient


def _forge_client() -> ForgeClient:
    token_provider = AsyncMock()
    token_provider.get_token = AsyncMock(return_value="test-token")
    return ForgeClient(token_provider=token_provider)


@pytest.mark.asyncio
async def test_create_issue_posts_json() -> None:
    client = _forge_client()
    http = MagicMock()
    created = MagicMock()
    created.raise_for_status = MagicMock()
    created.json.return_value = {"number": 3, "title": "t"}
    http.post = AsyncMock(return_value=created)
    client._client = http
    client._initialized = True

    data = await client.create_issue("acme", "widget", title="t", body="b", labels=["a"])
    assert data["number"] == 3
    http.post.assert_awaited()
    kwargs = http.post.await_args.kwargs
    assert kwargs["json"]["labels"] == ["a"]


@pytest.mark.asyncio
async def test_update_issue_status_patches_state_and_column() -> None:
    client = _forge_client()
    http = MagicMock()
    current = MagicMock()
    current.raise_for_status = MagicMock()
    current.json.return_value = {
        "number": 4,
        "state": "open",
        "labels": [{"name": "gateflow/column:Todo"}, {"name": "keep"}],
    }
    patched = MagicMock()
    patched.raise_for_status = MagicMock()
    patched.json.return_value = {"number": 4, "state": "closed", "labels": []}
    http.get = AsyncMock(return_value=current)
    http.patch = AsyncMock(return_value=patched)
    client._client = http
    client._initialized = True

    await client.update_issue_status("acme", "widget", 4, state="closed", column="Done")
    payload = http.patch.await_args.kwargs["json"]
    assert payload["state"] == "closed"
    assert "gateflow/column:Done" in payload["labels"]
    assert "gateflow/column:Todo" not in payload["labels"]
    assert "keep" in payload["labels"]


@pytest.mark.asyncio
async def test_link_pull_request_posts_comment() -> None:
    client = _forge_client()
    http = MagicMock()
    posted = MagicMock()
    posted.raise_for_status = MagicMock()
    posted.json.return_value = {"id": 99}
    http.post = AsyncMock(return_value=posted)
    client._client = http
    client._initialized = True

    link_ref = await client.link_pull_request("acme", "widget", 8, 12)
    assert link_ref == "99"
    body = http.post.await_args.kwargs["json"]["body"]
    assert "12" in body


@pytest.mark.asyncio
async def test_ensure_issue_on_project_posts_graphql() -> None:
    client = _forge_client()
    resolve_project = MagicMock()
    resolve_project.status_code = 200
    resolve_project.raise_for_status = MagicMock()
    resolve_project.json = MagicMock(
        return_value={"data": {"organization": {"projectV2": {"id": "PVT_proj"}}}}
    )
    resolve_issue = MagicMock()
    resolve_issue.status_code = 200
    resolve_issue.raise_for_status = MagicMock()
    resolve_issue.json = MagicMock(
        return_value={"data": {"repository": {"issue": {"id": "I_issue"}}}}
    )
    add_item = MagicMock()
    add_item.status_code = 200
    add_item.raise_for_status = MagicMock()
    add_item.json = MagicMock(
        return_value={"data": {"addProjectV2ItemById": {"item": {"id": "PVTI_1"}}}}
    )
    http = MagicMock()
    http.post = AsyncMock(side_effect=[resolve_project, resolve_issue, add_item])
    client._client = http
    client._initialized = True

    outcome = await client.ensure_issue_on_project(
        "acme",
        "widget",
        42,
        project_owner="acme",
        project_number=3,
    )
    assert outcome == "added"
    assert http.post.await_count == 3
    assert http.post.await_args_list[0].args[0] == "/graphql"


@pytest.mark.asyncio
async def test_ensure_issue_on_project_treats_already_as_success() -> None:
    client = _forge_client()
    resolve_project = MagicMock()
    resolve_project.raise_for_status = MagicMock()
    resolve_project.json = MagicMock(
        return_value={"data": {"organization": {"projectV2": {"id": "PVT_proj"}}}}
    )
    resolve_issue = MagicMock()
    resolve_issue.raise_for_status = MagicMock()
    resolve_issue.json = MagicMock(
        return_value={"data": {"repository": {"issue": {"id": "I_issue"}}}}
    )
    already = MagicMock()
    already.raise_for_status = MagicMock()
    already.json = MagicMock(
        return_value={"errors": [{"message": "The item is already in the project."}]}
    )
    http = MagicMock()
    http.post = AsyncMock(side_effect=[resolve_project, resolve_issue, already])
    client._client = http
    client._initialized = True

    outcome = await client.ensure_issue_on_project(
        "acme",
        "widget",
        42,
        project_owner="acme",
        project_number=3,
    )
    assert outcome == "already_on_project"


@pytest.mark.asyncio
async def test_ensure_sub_issue_posts_database_id() -> None:
    client = _forge_client()
    no_parent = MagicMock()
    no_parent.status_code = 404
    no_parent.raise_for_status = MagicMock()
    child = MagicMock()
    child.raise_for_status = MagicMock()
    child.json = MagicMock(
        return_value={"id": 9001, "number": 42, "title": "W0", "state": "open", "labels": []}
    )
    linked = MagicMock()
    linked.raise_for_status = MagicMock()
    linked.json = MagicMock(return_value={"number": 1})
    http = MagicMock()
    http.get = AsyncMock(side_effect=[no_parent, child])
    http.post = AsyncMock(return_value=linked)
    client._client = http
    client._initialized = True

    outcome = await client.ensure_sub_issue("acme", "widget", parent_number=1, child_number=42)
    assert outcome == "linked"
    assert http.post.await_args.args[0] == "/repos/acme/widget/issues/1/sub_issues"
    assert http.post.await_args.kwargs["json"]["sub_issue_id"] == 9001


def test_forge_client_source_has_no_gh_subprocess() -> None:
    """FR-25/26a inspection: ForgeClient must not invoke the GitHub CLI."""
    source = Path("src/infra_services/forge_client.py").read_text(encoding="utf-8")
    forbidden = (
        "import subprocess",
        "from subprocess",
        "Popen(",
        "os.system(",
        "shell=True",
        '"gh "',
        "'gh '",
    )
    for needle in forbidden:
        assert needle not in source, f"forbidden pattern in ForgeClient: {needle}"
