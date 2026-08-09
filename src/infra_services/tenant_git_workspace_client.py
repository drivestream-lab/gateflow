"""Clone/fetch tenant workspaces via subprocess git + stored PAT (INIT-GATEFLOW-012 W1).

FF-04: git CLI only — no Python git package. TF-01: serialize per org+repo.
"""

import asyncio
import base64
import os
import re
import subprocess
from pathlib import Path
from typing import Optional
from uuid import UUID

from injector import inject

from src.infra_services.base_infra_service import BaseInfraService
from src.logging import get_logger
from src.models.tenant_git_workspace_models import (
    TenantWorkspaceCredential,
    WorkspaceResolveModeType,
    WorkspaceResolveResult,
)

logger = get_logger()

_GITHUB_HOST = "github.com"
_REMOTE_ORG_REPO = re.compile(
    r"(?:https?://[^/]+/|git@[^:]+:)(?P<org>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?/?$",
    re.IGNORECASE,
)


class TenantGitWorkspaceError(Exception):
    """Named workspace resolve failure (mapped to 422 at business edge)."""

    def __init__(
        self,
        message: str,
        *,
        reason: str,
        org: str,
        repo: str,
    ) -> None:
        super().__init__(message)
        self.reason = reason
        self.org = org
        self.repo = repo


class TenantGitWorkspaceClient(BaseInfraService):
    """Resolve `{workspace_root}/{org}/{repo}` via clone or fetch-in-place."""

    @inject
    def __init__(self) -> None:
        super().__init__()
        self._initialized = False
        self._locks: dict[str, asyncio.Lock] = {}
        self._locks_guard = asyncio.Lock()

    async def initialize(self) -> None:
        self._initialized = True
        logger.info("TenantGitWorkspaceClient initialized")

    async def close(self) -> None:
        self._initialized = False

    async def health_check(self) -> bool:
        return self._initialized

    async def resolve_workspace(
        self,
        credential: TenantWorkspaceCredential,
        *,
        ref: Optional[str] = None,
    ) -> WorkspaceResolveResult:
        """Clone or fetch the registered repo under the tenant workspace_root.

        When ``ref`` is set, check out that ref after clone/fetch (INIT-013 FF-05).
        Never logs ``credential.pat``. Holds a per-org+repo lock for the call (TF-01).
        """
        org = credential.org.strip()
        repo = credential.repo.strip()
        if not org or not repo:
            raise TenantGitWorkspaceError(
                "org and repo are required for workspace resolve",
                reason="invalid_org_repo",
                org=org,
                repo=repo,
            )
        root = Path(credential.workspace_root)
        if not root.is_absolute():
            raise TenantGitWorkspaceError(
                "workspace_root must be an absolute path",
                reason="workspace_root_not_absolute",
                org=org,
                repo=repo,
            )
        cleaned_ref = ref.strip() if ref is not None and ref.strip() else None
        target = (root / org / repo).resolve()
        lock = await self._lock_for(org, repo)
        async with lock:
            return await self._resolve_locked(
                tenant_id=credential.tenant_id,
                pat=credential.pat,
                org=org,
                repo=repo,
                target=target,
                ref=cleaned_ref,
            )

    async def _resolve_locked(
        self,
        *,
        tenant_id: UUID,
        pat: str,
        org: str,
        repo: str,
        target: Path,
        ref: Optional[str] = None,
    ) -> WorkspaceResolveResult:
        rel_path = f"{org}/{repo}"
        if target.exists():
            if not self._is_valid_checkout(target, org=org, repo=repo):
                raise TenantGitWorkspaceError(
                    "Existing path is not a valid checkout of the expected remote",
                    reason="workspace_mismatch",
                    org=org,
                    repo=repo,
                )
            await self._git_fetch(target, pat=pat, org=org, repo=repo)
            if ref is not None:
                await self._checkout_ref(target, ref=ref, org=org, repo=repo)
            logger.info(
                "Tenant workspace fetched",
                tenant_id=str(tenant_id),
                org=org,
                repo=repo,
                mode=WorkspaceResolveModeType.FETCHED.value,
                path=rel_path,
                ref=ref,
            )
            return WorkspaceResolveResult(
                path=str(target),
                mode=WorkspaceResolveModeType.FETCHED,
            )

        target.parent.mkdir(parents=True, exist_ok=True)
        await self._git_clone(target, pat=pat, org=org, repo=repo)
        if ref is not None:
            await self._checkout_ref(target, ref=ref, org=org, repo=repo)
        logger.info(
            "Tenant workspace cloned",
            tenant_id=str(tenant_id),
            org=org,
            repo=repo,
            mode=WorkspaceResolveModeType.CLONED.value,
            path=rel_path,
            ref=ref,
        )
        return WorkspaceResolveResult(
            path=str(target),
            mode=WorkspaceResolveModeType.CLONED,
        )

    async def _checkout_ref(
        self,
        target: Path,
        *,
        ref: str,
        org: str,
        repo: str,
    ) -> None:
        """Check out ``ref`` or ``origin/{ref}`` in an existing checkout."""
        code, stderr = await self._run_git(["git", "-C", str(target), "checkout", "--force", ref])
        if code == 0:
            return
        code2, stderr2 = await self._run_git(
            [
                "git",
                "-C",
                str(target),
                "checkout",
                "--force",
                "-B",
                ref,
                f"origin/{ref}",
            ]
        )
        if code2 != 0:
            raise TenantGitWorkspaceError(
                f"git checkout failed for ref {ref!r}",
                reason=f"checkout_failed:{self._classify_git_failure(stderr2 or stderr)}",
                org=org,
                repo=repo,
            )

    async def _lock_for(self, org: str, repo: str) -> asyncio.Lock:
        key = f"{org.lower()}/{repo.lower()}"
        async with self._locks_guard:
            lock = self._locks.get(key)
            if lock is None:
                lock = asyncio.Lock()
                self._locks[key] = lock
            return lock

    def _is_valid_checkout(self, path: Path, *, org: str, repo: str) -> bool:
        if not path.is_dir() or not (path / ".git").exists():
            return False
        result = subprocess.run(
            ["git", "-C", str(path), "remote", "get-url", "origin"],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return False
        parsed = self._parse_org_repo(result.stdout.strip())
        if parsed is None:
            return False
        got_org, got_repo = parsed
        return got_org.lower() == org.lower() and got_repo.lower() == repo.lower()

    @staticmethod
    def _parse_org_repo(remote_url: str) -> Optional[tuple[str, str]]:
        cleaned = remote_url.strip()
        cleaned = re.sub(r"https?://[^@]+@", "https://", cleaned)
        match = _REMOTE_ORG_REPO.search(cleaned)
        if match is None:
            return None
        return match.group("org"), match.group("repo")

    def _auth_extra_header(self, pat: str) -> str:
        token = base64.b64encode(f"x-access-token:{pat}".encode("utf-8")).decode("ascii")
        return f"Authorization: Basic {token}"

    def _clone_url(self, org: str, repo: str) -> str:
        return f"https://{_GITHUB_HOST}/{org}/{repo}.git"

    async def _git_clone(self, target: Path, *, pat: str, org: str, repo: str) -> None:
        url = self._clone_url(org, repo)
        header = self._auth_extra_header(pat)
        code, _stderr = await self._run_git(
            [
                "git",
                "-c",
                f"http.extraHeader={header}",
                "clone",
                "--",
                url,
                str(target),
            ]
        )
        if code != 0:
            raise TenantGitWorkspaceError(
                "git clone failed for registered repo",
                reason=f"clone_failed:{self._classify_git_failure(_stderr)}",
                org=org,
                repo=repo,
            )

    async def _git_fetch(self, target: Path, *, pat: str, org: str, repo: str) -> None:
        header = self._auth_extra_header(pat)
        code, _stderr = await self._run_git(
            [
                "git",
                "-C",
                str(target),
                "-c",
                f"http.extraHeader={header}",
                "fetch",
                "--prune",
                "origin",
            ]
        )
        if code != 0:
            raise TenantGitWorkspaceError(
                "git fetch failed for registered repo",
                reason=f"fetch_failed:{self._classify_git_failure(_stderr)}",
                org=org,
                repo=repo,
            )

    async def checkout_branch(
        self,
        workspace_path: str | Path,
        *,
        branch: str,
        org: str,
        repo: str,
    ) -> None:
        """Check out ``origin/{branch}`` in an existing clone (REQ-19 composition)."""
        cleaned = branch.strip()
        if not cleaned:
            raise TenantGitWorkspaceError(
                "branch is required for workspace checkout",
                reason="invalid_branch",
                org=org,
                repo=repo,
            )
        target = Path(workspace_path)
        if not target.is_dir() or not (target / ".git").exists():
            raise TenantGitWorkspaceError(
                "workspace_path is not a git checkout",
                reason="checkout_not_a_repo",
                org=org,
                repo=repo,
            )
        code, stderr = await self._run_git(
            [
                "git",
                "-C",
                str(target),
                "checkout",
                "--force",
                "-B",
                cleaned,
                f"origin/{cleaned}",
            ]
        )
        if code != 0:
            raise TenantGitWorkspaceError(
                f"git checkout failed for branch {cleaned!r}",
                reason=f"checkout_failed:{self._classify_git_failure(stderr)}",
                org=org,
                repo=repo,
            )
        logger.info(
            "Tenant workspace checked out branch",
            org=org,
            repo=repo,
            branch=cleaned,
        )

    @staticmethod
    def _classify_git_failure(stderr: str) -> str:
        text = (stderr or "").lower()
        if "authentication" in text or "could not read username" in text or "403" in text:
            return "auth"
        if "not found" in text or "404" in text or "repository not found" in text:
            return "not_found"
        if "could not resolve host" in text or "network" in text or "timed out" in text:
            return "network"
        return "transport"

    async def _run_git(self, argv: list[str]) -> tuple[int, str]:
        env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
        proc = await asyncio.create_subprocess_exec(
            *argv,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )
        _stdout, stderr_b = await proc.communicate()
        stderr = (stderr_b or b"").decode("utf-8", errors="replace")
        redacted = re.sub(
            r"(Authorization:\s*Basic\s+)\S+",
            r"\1[REDACTED]",
            stderr,
            flags=re.IGNORECASE,
        )
        redacted = re.sub(r"x-access-token:[^@\s]+", "x-access-token:[REDACTED]", redacted)
        code = proc.returncode if proc.returncode is not None else 1
        return code, redacted


def get_tenant_git_workspace_client() -> TenantGitWorkspaceClient:
    from src.di.dependency_container import provide_service

    return provide_service(TenantGitWorkspaceClient)
