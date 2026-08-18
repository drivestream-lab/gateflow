"""Unit tests for TenantGitWorkspaceClient (INIT-GATEFLOW-012 W1 / REQ-10–14)."""

import asyncio
import subprocess
from pathlib import Path
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from src.infra_services.tenant_git_workspace_client import (
    TenantGitWorkspaceClient,
    TenantGitWorkspaceError,
)
from src.models.tenant_git_workspace_models import (
    DEFAULT_WORKSPACE_REF,
    TenantWorkspaceCredential,
    WorkspaceResolveModeType,
    resolve_workspace_ref,
)


def _cred(tmp_path: Path, *, org: str = "acme", repo: str = "widget") -> TenantWorkspaceCredential:
    return TenantWorkspaceCredential(
        tenant_id=uuid4(),
        workspace_root=str(tmp_path),
        pat="ghp_test_pat_not_real",
        org=org,
        repo=repo,
    )


def _init_remote_like_checkout(path: Path, *, org: str, repo: str) -> None:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True)
    subprocess.run(
        ["git", "remote", "add", "origin", f"https://github.com/{org}/{repo}.git"],
        cwd=path,
        check=True,
        capture_output=True,
    )


@pytest.mark.asyncio
async def test_resolve_clones_when_path_missing(tmp_path: Path) -> None:
    client = TenantGitWorkspaceClient()
    await client.initialize()
    cred = _cred(tmp_path)
    target = tmp_path / "acme" / "widget"

    async def fake_clone(path: Path, *, pat: str, org: str, repo: str) -> None:
        _ = pat
        path.mkdir(parents=True, exist_ok=True)
        _init_remote_like_checkout(path, org=org, repo=repo)

    with patch.object(client, "_git_clone", new=AsyncMock(side_effect=fake_clone)) as clone:
        with patch.object(client, "_git_fetch", new=AsyncMock()) as fetch:
            with patch.object(client, "_checkout_ref", new=AsyncMock()) as checkout:
                result = await client.resolve_workspace(cred)

    assert result.mode == WorkspaceResolveModeType.CLONED
    assert result.path == str(target.resolve())
    clone.assert_awaited_once()
    fetch.assert_not_awaited()
    checkout.assert_awaited_once()
    assert checkout.await_args is not None
    assert checkout.await_args.kwargs["ref"] == DEFAULT_WORKSPACE_REF


@pytest.mark.asyncio
async def test_resolve_fetches_when_valid_checkout_exists(tmp_path: Path) -> None:
    client = TenantGitWorkspaceClient()
    await client.initialize()
    cred = _cred(tmp_path)
    target = tmp_path / "acme" / "widget"
    _init_remote_like_checkout(target, org="acme", repo="widget")

    with patch.object(client, "_git_clone", new=AsyncMock()) as clone:
        with patch.object(client, "_git_fetch", new=AsyncMock()) as fetch:
            with patch.object(client, "_checkout_ref", new=AsyncMock()) as checkout:
                result = await client.resolve_workspace(cred)

    assert result.mode == WorkspaceResolveModeType.FETCHED
    assert result.path == str(target.resolve())
    fetch.assert_awaited_once()
    clone.assert_not_awaited()
    checkout.assert_awaited_once()
    assert checkout.await_args is not None
    assert checkout.await_args.kwargs["ref"] == DEFAULT_WORKSPACE_REF


@pytest.mark.asyncio
async def test_resolve_mismatch_leaves_tree_untouched(tmp_path: Path) -> None:
    client = TenantGitWorkspaceClient()
    await client.initialize()
    cred = _cred(tmp_path)
    target = tmp_path / "acme" / "widget"
    _init_remote_like_checkout(target, org="other", repo="repo")
    marker = target / "KEEP_ME.txt"
    marker.write_text("untouched", encoding="utf-8")

    with pytest.raises(TenantGitWorkspaceError) as exc_info:
        await client.resolve_workspace(cred)

    assert exc_info.value.reason == "workspace_mismatch"
    assert marker.read_text(encoding="utf-8") == "untouched"
    assert (target / ".git").exists()


@pytest.mark.asyncio
async def test_resolve_non_git_dir_is_mismatch(tmp_path: Path) -> None:
    client = TenantGitWorkspaceClient()
    await client.initialize()
    cred = _cred(tmp_path)
    target = tmp_path / "acme" / "widget"
    target.mkdir(parents=True)
    (target / "noise.txt").write_text("x", encoding="utf-8")

    with pytest.raises(TenantGitWorkspaceError) as exc_info:
        await client.resolve_workspace(cred)

    assert exc_info.value.reason == "workspace_mismatch"
    assert (target / "noise.txt").exists()


@pytest.mark.asyncio
async def test_per_repo_lock_serializes_concurrent_resolves(tmp_path: Path) -> None:
    client = TenantGitWorkspaceClient()
    await client.initialize()
    cred = _cred(tmp_path)
    active = 0
    max_active = 0
    gate = asyncio.Event()

    async def slow_clone(path: Path, *, pat: str, org: str, repo: str) -> None:
        nonlocal active, max_active
        _ = pat, org, repo
        active += 1
        max_active = max(max_active, active)
        await gate.wait()
        path.mkdir(parents=True, exist_ok=True)
        _init_remote_like_checkout(path, org="acme", repo="widget")
        active -= 1

    async def slow_fetch(path: Path, *, pat: str, org: str, repo: str) -> None:
        nonlocal active, max_active
        _ = path, pat, org, repo
        active += 1
        max_active = max(max_active, active)
        await gate.wait()
        active -= 1

    with patch.object(client, "_git_clone", new=AsyncMock(side_effect=slow_clone)):
        with patch.object(client, "_git_fetch", new=AsyncMock(side_effect=slow_fetch)):
            with patch.object(client, "_checkout_ref", new=AsyncMock()):
                t1 = asyncio.create_task(client.resolve_workspace(cred))
                t2 = asyncio.create_task(client.resolve_workspace(cred))
                await asyncio.sleep(0.05)
                assert max_active == 1
                gate.set()
                results = await asyncio.gather(t1, t2)

    assert all(
        r.mode in {WorkspaceResolveModeType.CLONED, WorkspaceResolveModeType.FETCHED}
        for r in results
    )
    assert max_active == 1


def test_parse_org_repo_strips_credentials() -> None:
    parsed = TenantGitWorkspaceClient._parse_org_repo(
        "https://x-access-token:SECRET@github.com/Acme/Widget.git"
    )
    assert parsed == ("Acme", "Widget")


def test_no_python_git_dependency_in_module_source() -> None:
    source = Path("src/infra_services/tenant_git_workspace_client.py").read_text(encoding="utf-8")
    assert "GitPython" not in source
    assert "pygit2" not in source
    assert "import git" not in source


@pytest.mark.asyncio
async def test_resolve_with_ref_checks_out_after_clone(tmp_path: Path) -> None:
    client = TenantGitWorkspaceClient()
    await client.initialize()
    cred = _cred(tmp_path)

    async def fake_clone(path: Path, *, pat: str, org: str, repo: str) -> None:
        _ = pat
        path.mkdir(parents=True, exist_ok=True)
        _init_remote_like_checkout(path, org=org, repo=repo)

    with patch.object(client, "_git_clone", new=AsyncMock(side_effect=fake_clone)):
        with patch.object(client, "_checkout_ref", new=AsyncMock()) as checkout:
            result = await client.resolve_workspace(cred, ref="main")

    assert result.mode == WorkspaceResolveModeType.CLONED
    checkout.assert_awaited_once()
    assert checkout.await_args is not None
    assert checkout.await_args.kwargs["ref"] == "main"


@pytest.mark.asyncio
async def test_resolve_without_ref_syncs_origin_develop(tmp_path: Path) -> None:
    client = TenantGitWorkspaceClient()
    await client.initialize()
    cred = _cred(tmp_path)

    async def fake_clone(path: Path, *, pat: str, org: str, repo: str) -> None:
        _ = pat
        path.mkdir(parents=True, exist_ok=True)
        _init_remote_like_checkout(path, org=org, repo=repo)

    with patch.object(client, "_git_clone", new=AsyncMock(side_effect=fake_clone)):
        with patch.object(client, "_checkout_ref", new=AsyncMock()) as checkout:
            await client.resolve_workspace(cred)

    checkout.assert_awaited_once()
    assert checkout.await_args is not None
    assert checkout.await_args.kwargs["ref"] == DEFAULT_WORKSPACE_REF


def test_resolve_workspace_ref_defaults_to_develop() -> None:
    assert resolve_workspace_ref(None) == DEFAULT_WORKSPACE_REF
    assert resolve_workspace_ref("") == DEFAULT_WORKSPACE_REF
    assert resolve_workspace_ref("   ") == DEFAULT_WORKSPACE_REF
    assert resolve_workspace_ref("main") == "main"


@pytest.mark.asyncio
async def test_checkout_branch_invokes_origin_tracking(tmp_path: Path) -> None:
    """REQ-19 companion: checkout uses origin/{branch} after clone/fetch."""
    client = TenantGitWorkspaceClient()
    await client.initialize()
    target = tmp_path / "acme" / "widget"
    _init_remote_like_checkout(target, org="acme", repo="widget")
    captured: list[list[str]] = []

    async def fake_run(argv: list[str]) -> tuple[int, str]:
        captured.append(list(argv))
        return 0, ""

    with patch.object(client, "_run_git", side_effect=fake_run):
        await client.checkout_branch(
            target,
            branch="feature/INIT-ACME-001-w2-x",
            org="acme",
            repo="widget",
        )

    assert captured
    assert "checkout" in captured[0]
    assert "origin/feature/INIT-ACME-001-w2-x" in captured[0]


@pytest.mark.asyncio
async def test_resolve_inits_submodules_after_checkout(tmp_path: Path) -> None:
    """REQ-14: committed sub-projects are initialized after checkout."""
    client = TenantGitWorkspaceClient()
    await client.initialize()
    cred = _cred(tmp_path)
    order: list[str] = []

    async def fake_clone(path: Path, *, pat: str, org: str, repo: str) -> None:
        _ = pat
        path.mkdir(parents=True, exist_ok=True)
        _init_remote_like_checkout(path, org=org, repo=repo)
        (path / ".gitmodules").write_text(
            '[submodule "prayog-skills"]\n\tpath = prayog-skills\n',
            encoding="utf-8",
        )

    async def fake_checkout(path: Path, *, ref: str, org: str, repo: str) -> None:
        _ = path, ref, org, repo
        order.append("checkout")

    async def fake_submodules(path: Path, *, pat: str, org: str, repo: str) -> None:
        _ = path, pat, org, repo
        order.append("submodule")

    with patch.object(client, "_git_clone", new=AsyncMock(side_effect=fake_clone)):
        with patch.object(client, "_checkout_ref", new=AsyncMock(side_effect=fake_checkout)):
            with patch.object(
                client, "_git_submodule_update", new=AsyncMock(side_effect=fake_submodules)
            ):
                await client.resolve_workspace(cred)

    assert order == ["checkout", "submodule"]


@pytest.mark.asyncio
async def test_resolve_skips_submodules_when_gitmodules_absent(tmp_path: Path) -> None:
    client = TenantGitWorkspaceClient()
    await client.initialize()
    cred = _cred(tmp_path)

    async def fake_clone(path: Path, *, pat: str, org: str, repo: str) -> None:
        _ = pat
        path.mkdir(parents=True, exist_ok=True)
        _init_remote_like_checkout(path, org=org, repo=repo)

    with patch.object(client, "_git_clone", new=AsyncMock(side_effect=fake_clone)):
        with patch.object(client, "_checkout_ref", new=AsyncMock()):
            with patch.object(client, "_run_git", new=AsyncMock()) as run_git:
                await client.resolve_workspace(cred)

    run_git.assert_not_awaited()


@pytest.mark.asyncio
async def test_resolve_fetch_inits_submodules(tmp_path: Path) -> None:
    client = TenantGitWorkspaceClient()
    await client.initialize()
    cred = _cred(tmp_path)
    target = tmp_path / "acme" / "widget"
    _init_remote_like_checkout(target, org="acme", repo="widget")
    (target / ".gitmodules").write_text(
        '[submodule "prayog-skills"]\n\tpath = prayog-skills\n',
        encoding="utf-8",
    )
    captured: list[list[str]] = []

    async def fake_run(argv: list[str]) -> tuple[int, str]:
        captured.append(list(argv))
        return 0, ""

    with patch.object(client, "_git_fetch", new=AsyncMock()):
        with patch.object(client, "_checkout_ref", new=AsyncMock()):
            with patch.object(client, "_run_git", side_effect=fake_run):
                await client.resolve_workspace(cred)

    assert captured
    assert "submodule" in captured[0]
    assert "--init" in captured[0]
    assert "--recursive" in captured[0]
    header = next(arg for arg in captured[0] if arg.startswith("http.extraHeader="))
    assert "REDACTED" not in header
    assert "Basic" in header


@pytest.mark.asyncio
async def test_submodule_failure_is_named(tmp_path: Path) -> None:
    client = TenantGitWorkspaceClient()
    await client.initialize()
    cred = _cred(tmp_path)

    async def fake_clone(path: Path, *, pat: str, org: str, repo: str) -> None:
        _ = pat
        path.mkdir(parents=True, exist_ok=True)
        _init_remote_like_checkout(path, org=org, repo=repo)
        (path / ".gitmodules").write_text(
            '[submodule "prayog-skills"]\n\tpath = prayog-skills\n',
            encoding="utf-8",
        )

    with patch.object(client, "_git_clone", new=AsyncMock(side_effect=fake_clone)):
        with patch.object(client, "_checkout_ref", new=AsyncMock()):
            with patch.object(
                client, "_run_git", new=AsyncMock(return_value=(1, "Authentication failed"))
            ):
                with pytest.raises(TenantGitWorkspaceError) as exc_info:
                    await client.resolve_workspace(cred)

    assert exc_info.value.reason == "submodule_failed:auth"
