"""LaunchpadClient — harness-readiness check (INIT-GATEFLOW-012 W3 / REQ-20–21).

CTR-03 / A-3: filesystem contract only — require ``.harness-pin.yaml`` and
``.harness/`` under the workspace. Cache/skip lives in tenant_repos via the
business layer (REQ-22).
"""

from pathlib import Path

from injector import inject

from src.infra_services.base_infra_service import BaseInfraService
from src.logging import get_logger

logger = get_logger()

_PIN_FILE = ".harness-pin.yaml"
_HARNESS_DIR = ".harness"


class HarnessReadinessError(Exception):
    """Named harness readiness failure (mapped to 422 at business edge)."""

    def __init__(
        self,
        message: str,
        *,
        reason: str,
        missing: list[str],
        workspace_path: str,
    ) -> None:
        super().__init__(message)
        self.reason = reason
        self.missing = list(missing)
        self.workspace_path = workspace_path


class LaunchpadClient(BaseInfraService):
    """Verify harness artifacts in a workspace before coding-hop dispatch."""

    @inject
    def __init__(self) -> None:
        super().__init__()
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True
        logger.info("LaunchpadClient initialized")

    async def close(self) -> None:
        self._initialized = False

    async def health_check(self) -> bool:
        return self._initialized

    async def sync_harness(self, workspace_path: str) -> None:
        """Require harness pin + ``.harness/`` directory (REQ-21).

        Raises ``FileNotFoundError`` when the workspace path is missing.
        Raises ``HarnessReadinessError`` when required artifacts are absent.
        """
        path = Path(workspace_path)
        if not path.is_dir():
            raise FileNotFoundError(f"Workspace path not found: {workspace_path}")

        missing: list[str] = []
        pin = path / _PIN_FILE
        harness_dir = path / _HARNESS_DIR
        if not pin.is_file():
            missing.append(_PIN_FILE)
        if not harness_dir.is_dir():
            missing.append(_HARNESS_DIR)
        if missing:
            raise HarnessReadinessError(
                "Workspace is missing required harness artifacts",
                reason="harness_artifacts_missing",
                missing=missing,
                workspace_path=str(path.resolve()),
            )
        logger.info(
            "Launchpad harness readiness ok",
            workspace_path=str(path.resolve()),
            pin_file=_PIN_FILE,
            harness_dir=_HARNESS_DIR,
        )


def get_launchpad_client() -> LaunchpadClient:
    from src.di.dependency_container import provide_service

    return provide_service(LaunchpadClient)
