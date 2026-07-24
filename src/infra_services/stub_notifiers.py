"""Honest stub notifier adapters (Slack / Teams) — not implemented."""

from injector import inject

from src.infra_services.base_infra_service import BaseInfraService
from src.logging import get_logger

logger = get_logger()


class SlackNotifierStub(BaseInfraService):
    """Slack notifier stub — registered, not implemented (FR-23)."""

    ADAPTER_ID = "slack"

    @inject
    def __init__(self) -> None:
        super().__init__()
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True
        logger.info("SlackNotifierStub registered as stub")

    async def close(self) -> None:
        self._initialized = False

    async def health_check(self) -> bool:
        return self._initialized


class TeamsNotifierStub(BaseInfraService):
    """Teams notifier stub — registered, not implemented (FR-23)."""

    ADAPTER_ID = "teams"

    @inject
    def __init__(self) -> None:
        super().__init__()
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True
        logger.info("TeamsNotifierStub registered as stub")

    async def close(self) -> None:
        self._initialized = False

    async def health_check(self) -> bool:
        return self._initialized
