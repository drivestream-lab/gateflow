"""LaunchpadApplyHarnessClient — service-mode apply-harness (Launchpad >= 0.5.35).

Setup-on-select only. Status remains inspect-only on LaunchpadStatusClient.
Do not git-add / commit after apply (hubs are gitignored; pin/AGENTS may change).
"""

from __future__ import annotations

from pathlib import Path

from injector import inject
from pydantic import ValidationError

from src.configs.app_settings import AppSettings
from src.infra_services.base_infra_service import BaseInfraService
from src.infra_services.launchpad_cli_runtime import (
    launchpad_binary_available,
    resolve_launchpad_config_dir,
    resolve_launchpad_workspace_root,
    run_launchpad_cli,
)
from src.logging import get_logger
from src.models.programme_readiness_models import (
    LaunchpadApplyHarnessVerdict,
    LaunchpadCommandReport,
)

logger = get_logger()


class LaunchpadApplyHarnessError(Exception):
    """Named apply-harness tool failure (mapped at business edge)."""

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


class LaunchpadApplyHarnessClient(BaseInfraService):
    """Run Launchpad ``apply-harness --apply`` against a cloned app repo."""

    @inject
    def __init__(self) -> None:
        super().__init__()
        self._settings = AppSettings.get_instance()
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True
        logger.info(
            "LaunchpadApplyHarnessClient initialized",
            launchpad_cli_path=self._settings.launchpad_cli_path,
        )

    async def close(self) -> None:
        self._initialized = False

    async def health_check(self) -> bool:
        if not self._initialized:
            return False
        return launchpad_binary_available(self._settings.launchpad_cli_path)

    def build_apply_argv(
        self,
        *,
        meta_config_dir: str,
        workspace: str,
        repo: str,
    ) -> list[str]:
        """Service-mode apply argv (Launchpad >= 0.5.35). PAT never on argv."""
        cli = self._settings.launchpad_cli_path.strip() or "launchpad"
        argv = [
            cli,
            "apply-harness",
            "--no-client",
            "--config-dir",
            meta_config_dir,
            "--workspace",
            workspace,
            "--repo",
            repo,
            "--apply",
            "--format",
            "json",
        ]
        self._assert_apply_argv(argv)
        return argv

    async def apply_harness(
        self,
        *,
        repo_workspace: str,
        meta_config_dir: str,
        org: str,
        repo: str,
        pat: str,
    ) -> LaunchpadApplyHarnessVerdict:
        """Materialize harness on an existing clone. Never commit."""
        if not launchpad_binary_available(self._settings.launchpad_cli_path):
            logger.error(
                "Launchpad apply-harness tool unavailable",
                reason="tool_unavailable",
                org=org,
                repo=repo,
                launchpad_cli_path=self._settings.launchpad_cli_path,
            )
            raise LaunchpadApplyHarnessError(
                "Launchpad CLI is unavailable or not executable",
                reason="tool_unavailable",
                org=org,
                repo=repo,
            )

        repo_path = Path(repo_workspace)
        meta_path = Path(meta_config_dir)
        if not repo_path.is_dir():
            raise LaunchpadApplyHarnessError(
                "Repo workspace path is missing for apply-harness",
                reason="workspace_path_missing",
                org=org,
                repo=repo,
            )
        if not meta_path.is_dir():
            raise LaunchpadApplyHarnessError(
                "Programme meta config dir is missing for apply-harness",
                reason="meta_config_missing",
                org=org,
                repo=repo,
            )
        cleaned_pat = pat.strip()
        if not cleaned_pat:
            raise LaunchpadApplyHarnessError(
                "Programme PAT is required for Launchpad apply-harness",
                reason="programme_pat_missing",
                org=org,
                repo=repo,
            )
        config_dir = resolve_launchpad_config_dir(meta_path)
        workspace = resolve_launchpad_workspace_root(repo_path)

        argv = self.build_apply_argv(
            meta_config_dir=str(config_dir.resolve()),
            workspace=str(workspace.resolve()),
            repo=repo,
        )
        code, stdout, _stderr = await run_launchpad_cli(argv, github_token=cleaned_pat)
        try:
            report = LaunchpadCommandReport.from_stdout(stdout)
        except (ValueError, ValidationError) as exc:
            logger.warning(
                "Launchpad apply-harness JSON parse failed",
                org=org,
                repo=repo,
                exit_code=code,
                error_type=type(exc).__name__,
            )
            raise LaunchpadApplyHarnessError(
                "Launchpad apply-harness JSON stdout could not be parsed",
                reason="json_parse_failed",
                org=org,
                repo=repo,
            ) from exc

        if code == 0 and report.ok:
            logger.info(
                "Launchpad apply-harness ok",
                org=org,
                repo=repo,
            )
            return LaunchpadApplyHarnessVerdict(ok=True)

        reason = report.named_apply_reason()
        logger.warning(
            "Launchpad apply-harness failed",
            org=org,
            repo=repo,
            reason=reason,
            exit_code=code,
            failing_checks=", ".join(report.failing_check_ids()) or None,
        )
        return LaunchpadApplyHarnessVerdict(ok=False, reason=reason)

    @staticmethod
    def _assert_apply_argv(argv: list[str]) -> None:
        lowered = [t.lower() for t in argv[1:]]
        if "apply-harness" not in lowered:
            raise LaunchpadApplyHarnessError(
                "Launchpad argv must include apply-harness subcommand",
                reason="argv_guard",
            )
        if "--apply" not in {t.lower() for t in argv[1:]}:
            raise LaunchpadApplyHarnessError(
                "Launchpad apply-harness argv must include --apply",
                reason="argv_guard",
            )
        if "--token" in lowered or any(t.startswith("--token=") for t in lowered):
            raise LaunchpadApplyHarnessError(
                "Launchpad argv must not include a token flag",
                reason="argv_guard",
            )


def get_launchpad_apply_harness_client() -> LaunchpadApplyHarnessClient:
    from src.di.dependency_container import provide_service

    return provide_service(LaunchpadApplyHarnessClient)
