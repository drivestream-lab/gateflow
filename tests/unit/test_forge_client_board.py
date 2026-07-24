"""Unit tests for ForgeClient board ops and gh-free production path (FR-24/25/26a)."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.infra_services.forge_client import ForgeClient


@pytest.mark.asyncio
async def test_create_issue_posts_json() -> None:
    client = ForgeClient()
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
    client = ForgeClient()
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
    client = ForgeClient()
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


def test_forge_client_source_has_no_gh_subprocess() -> None:
    """FR-25/26a inspection: ForgeClient must not invoke the GitHub CLI."""
    source = Path("src/infra_services/forge_client.py").read_text(encoding="utf-8")
    forbidden = (
        "import subprocess",
        "from subprocess",
        "Popen(",
        "os.system(",
        'shutil.which("gh")',
        "shutil.which('gh')",
        '["gh"',
        "['gh'",
    )
    for token in forbidden:
        assert token not in source, f"forbidden transport token found: {token}"
