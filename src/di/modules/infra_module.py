"""Infrastructure services module for dependency injection."""

from injector import Module, singleton

from src.database.postgres.connection_manager import PostgresConnectionManager
from src.database.redis.connection_manager import RedisConnectionManager
from src.infra_services.cursor_agent_runner import CursorAgentRunner
from src.infra_services.forge_client import ForgeClient
from src.infra_services.launchpad_client import LaunchpadClient
from src.infra_services.postgres_service import PostgresService
from src.infra_services.redis_service import RedisService
from src.infra_services.stub_agent_runners import ClaudeCodeAgentRunner, OpenCodeAgentRunner
from src.infra_services.stub_notifiers import SlackNotifierStub, TeamsNotifierStub
from src.infra_services.telemetry_service import TelemetryService
from src.logging import get_logger

logger = get_logger()


class InfraModule(Module):
    """Register core infrastructure services."""

    def configure(self, binder) -> None:
        logger.info("Configuring infrastructure services module")
        binder.bind(PostgresConnectionManager, to=PostgresConnectionManager, scope=singleton)
        binder.bind(RedisConnectionManager, to=RedisConnectionManager, scope=singleton)
        binder.bind(PostgresService, to=PostgresService, scope=singleton)
        binder.bind(RedisService, to=RedisService, scope=singleton)
        binder.bind(TelemetryService, scope=singleton)
        binder.bind(ForgeClient, to=ForgeClient, scope=singleton)
        binder.bind(LaunchpadClient, to=LaunchpadClient, scope=singleton)
        binder.bind(CursorAgentRunner, to=CursorAgentRunner, scope=singleton)
        binder.bind(OpenCodeAgentRunner, to=OpenCodeAgentRunner, scope=singleton)
        binder.bind(ClaudeCodeAgentRunner, to=ClaudeCodeAgentRunner, scope=singleton)
        binder.bind(SlackNotifierStub, to=SlackNotifierStub, scope=singleton)
        binder.bind(TeamsNotifierStub, to=TeamsNotifierStub, scope=singleton)
        logger.debug("Infrastructure services module configured")
