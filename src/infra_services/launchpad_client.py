"""LaunchpadClient — harness sync infra slot (W1: log + no-op)."""

from pathlib import Path

from injector import inject

from src.infra_services.base_infra_service import BaseInfraService
from src.logging import get_logger

logger = get_logger()


class LaunchpadClient(BaseInfraService):
    """Sync pinned harness in workspace; W1 stub succeeds when path exists."""

    @inject
    def __init__(self) -> None:
        super().__init__()
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True
        logger.info("LaunchpadClient initialized (W1 no-op harness sync)")

    async def close(self) -> None:
        self._initialized = False

    async def health_check(self) -> bool:
        return self._initialized

    async def sync_harness(self, workspace_path: str) -> None:
        """Verify workspace exists; W1 logs and returns without subprocess."""
        path = Path(workspace_path)
        if not path.is_dir():
            raise FileNotFoundError(f"Workspace path not found: {workspace_path}")
        logger.info(
            "Launchpad harness sync skipped (W1 stub)",
            workspace_path=workspace_path,
        )


def get_launchpad_client() -> LaunchpadClient:
    from src.di.dependency_container import provide_service

    return provide_service(LaunchpadClient)
