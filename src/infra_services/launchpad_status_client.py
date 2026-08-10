"""LaunchpadStatusClient — inspect-only Launchpad status (INIT-GATEFLOW-013 W3).

ADR-013 Option B: separate from LaunchpadClient.sync_harness (filesystem).
REQ-18: argv never includes apply/install/mutate verbs.
REQ-20: tool_unavailable is distinct from repo not-ready.
"""

from __future__ import annotations

import asyncio
import os
import shutil
from pathlib import Path

from injector import inject

from src.configs.app_settings import AppSettings
from src.infra_services.base_infra_service import BaseInfraService
from src.logging import get_logger
from src.models.programme_readiness_models import (
    LaunchpadStatusVerdict,
    LaunchpadStatusVerdictType,
)

logger = get_logger()

# Forbidden argv tokens — never pass these to Launchpad from this client (REQ-18).
_FORBIDDEN_ARGV = frozenset(
    {
        "apply",
        "install",
        "fix",
        "upgrade",
        "init",
        "sync",
        "write",
        "mutate",
    }
)


class LaunchpadStatusError(Exception):
    """Named status inspect failure (mapped at business edge)."""

    def __init__(
        self,
        message: str,
        *,
        reason: str,
        org: str | None = None,
        repo: str | None = None,
    ) -> None:
        super().__init__(message)
        self.reason = reason
        self.org = org
        self.repo = repo


class LaunchpadStatusClient(BaseInfraService):
    """Run Launchpad ``status`` against a repo workspace + programme meta config."""

    @inject
    def __init__(self) -> None:
        super().__init__()
        self._settings = AppSettings.get_instance()
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True
        logger.info(
            "LaunchpadStatusClient initialized",
            launchpad_cli_path=self._settings.launchpad_cli_path,
        )

    async def close(self) -> None:
        self._initialized = False

    async def health_check(self) -> bool:
        if not self._initialized:
            return False
        return self._binary_available()

    def build_status_argv(
        self,
        *,
        repo_workspace: str,
        meta_config_dir: str,
        org: str,
        repo: str,
    ) -> list[str]:
        """Construct inspect-only argv (no apply). Raises if forbidden tokens slip in."""
        cli = self._settings.launchpad_cli_path.strip() or "launchpad"
        argv = [
            cli,
            "status",
            "--config-dir",
            meta_config_dir,
            "--repo",
            f"{org}/{repo}",
            "--meta",
            repo_workspace,
        ]
        self._assert_inspect_only(argv)
        return argv

    async def inspect_status(
        self,
        *,
        repo_workspace: str,
        meta_config_dir: str,
        org: str,
        repo: str,
    ) -> LaunchpadStatusVerdict:
        """Ask Launchpad status only — never apply (REQ-17/18/20)."""
        if not self._binary_available():
            logger.error(
                "Launchpad status tool unavailable",
                reason="tool_unavailable",
                org=org,
                repo=repo,
                launchpad_cli_path=self._settings.launchpad_cli_path,
            )
            raise LaunchpadStatusError(
                "Launchpad CLI is unavailable or not executable",
                reason="tool_unavailable",
                org=org,
                repo=repo,
            )

        repo_path = Path(repo_workspace)
        meta_path = Path(meta_config_dir)
        if not repo_path.is_dir():
            raise LaunchpadStatusError(
                "Repo workspace path is missing for status inspect",
                reason="workspace_path_missing",
                org=org,
                repo=repo,
            )
        if not meta_path.is_dir():
            raise LaunchpadStatusError(
                "Programme meta config dir is missing for status inspect",
                reason="meta_config_missing",
                org=org,
                repo=repo,
            )

        argv = self.build_status_argv(
            repo_workspace=str(repo_path.resolve()),
            meta_config_dir=str(meta_path.resolve()),
            org=org,
            repo=repo,
        )
        code, stderr = await self._run(argv)
        if code == 0:
            logger.info(
                "Launchpad status ready",
                org=org,
                repo=repo,
                evaluator="launchpad_status",
            )
            return LaunchpadStatusVerdict(
                verdict_type=LaunchpadStatusVerdictType.READY,
                ready=True,
            )

        reason = self._classify_failure(stderr)
        logger.warning(
            "Launchpad status not ready",
            org=org,
            repo=repo,
            reason=reason,
            exit_code=code,
        )
        return LaunchpadStatusVerdict(
            verdict_type=LaunchpadStatusVerdictType.NOT_READY,
            reason=reason,
            ready=False,
        )

    def _binary_available(self) -> bool:
        cli = self._settings.launchpad_cli_path.strip() or "launchpad"
        path = Path(cli)
        if path.is_file() and os.access(path, os.X_OK):
            return True
        return shutil.which(cli) is not None

    @staticmethod
    def _assert_inspect_only(argv: list[str]) -> None:
        tokens = {t.lower().lstrip("-") for t in argv[1:]}
        banned = tokens & _FORBIDDEN_ARGV
        if banned:
            raise LaunchpadStatusError(
                f"Forbidden Launchpad argv tokens: {sorted(banned)}",
                reason="argv_guard",
            )
        if "status" not in {t.lower() for t in argv[1:]}:
            raise LaunchpadStatusError(
                "Launchpad argv must include status subcommand",
                reason="argv_guard",
            )

    @staticmethod
    def _classify_failure(stderr: str) -> str:
        text = (stderr or "").lower()
        if "not found" in text or "no such file" in text:
            return "repo_not_ready:missing"
        if "pin" in text or "harness" in text:
            return "repo_not_ready:harness"
        return "repo_not_ready"

    async def _run(self, argv: list[str]) -> tuple[int, str]:
        proc = await asyncio.create_subprocess_exec(
            *argv,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _stdout, stderr_b = await proc.communicate()
        code = proc.returncode if proc.returncode is not None else 1
        stderr = (stderr_b or b"").decode("utf-8", errors="replace")
        return code, stderr


def get_launchpad_status_client() -> LaunchpadStatusClient:
    from src.di.dependency_container import provide_service

    return provide_service(LaunchpadStatusClient)
