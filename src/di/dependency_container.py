"""Dependency injection container for gateflow."""

from typing import Any, Optional, Type, TypeVar

from injector import Injector

from src.configs.app_settings import AppSettings
from src.infra_services.postgres_service import PostgresService
from src.infra_services.redis_service import RedisService
from src.infra_services.telemetry_service import TelemetryService
from src.logging import get_logger

T = TypeVar("T")
_injector: Optional[Injector] = None
logger = get_logger()

# Postgres first — business services depend on session factory from PostgresService.
_INFRA_SERVICE_TYPES: tuple[type, ...] = (
    PostgresService,
    RedisService,
    TelemetryService,
)

_BUSINESS_SERVICE_TYPES: tuple[type, ...] = ()


def configure_container() -> Injector:
    from src.business_services.adapter_registry import AdapterRegistry
    from src.business_services.board_service import BoardService
    from src.business_services.checkpoint_evidence_service import CheckpointEvidenceService
    from src.business_services.forge_action_service import ForgeActionService
    from src.business_services.handoff_reader import HandoffReader
    from src.business_services.job_worker_service import JobWorkerService
    from src.business_services.learning_ingest_service import LearningIngestService
    from src.business_services.meta_pr_intake import MetaPrIntakeService
    from src.business_services.metrics_emitter import MetricsEmitter
    from src.business_services.notifier import Notifier
    from src.business_services.policy_engine import PolicyEngine
    from src.business_services.prompt_resolver import PromptResolver
    from src.business_services.run_orchestrator import RunOrchestrator
    from src.business_services.slot_validator import SlotValidator
    from src.business_services.tenant_service import TenantService
    from src.business_services.trigger_router import TriggerRouter
    from src.business_services.wave_start_service import WaveStartService
    from src.business_services.webhook_ingress_service import WebhookIngressService
    from src.business_services.workflow_engine import WorkflowEngine
    from src.di.modules.business_services_module import BusinessServicesModule
    from src.di.modules.config_module import ConfigModule
    from src.di.modules.infra_module import InfraModule
    from src.di.modules.repository_module import RepositoryModule
    from src.infra_services.cursor_agent_runner import CursorAgentRunner
    from src.infra_services.forge_client import ForgeClient
    from src.infra_services.github_pat_probe import GithubPatProbe
    from src.infra_services.launchpad_client import LaunchpadClient
    from src.infra_services.stub_agent_runners import ClaudeCodeAgentRunner, OpenCodeAgentRunner
    from src.infra_services.stub_notifiers import SlackNotifierStub, TeamsNotifierStub
    from src.infra_services.tenant_git_workspace_client import TenantGitWorkspaceClient

    settings = AppSettings.get_instance()
    global _injector
    if _injector is None:
        logger.info("Configuring DI container", environment=str(settings.environment))
        _injector = Injector(
            [
                ConfigModule(),
                InfraModule(),
                RepositoryModule(),
                BusinessServicesModule(),
            ]
        )
        global _INFRA_SERVICE_TYPES, _BUSINESS_SERVICE_TYPES
        _INFRA_SERVICE_TYPES = (
            PostgresService,
            RedisService,
            TelemetryService,
            ForgeClient,
            GithubPatProbe,
            TenantGitWorkspaceClient,
            LaunchpadClient,
            CursorAgentRunner,
            OpenCodeAgentRunner,
            ClaudeCodeAgentRunner,
            SlackNotifierStub,
            TeamsNotifierStub,
        )
        _BUSINESS_SERVICE_TYPES = (
            WebhookIngressService,
            JobWorkerService,
            HandoffReader,
            WorkflowEngine,
            TriggerRouter,
            PolicyEngine,
            Notifier,
            MetricsEmitter,
            AdapterRegistry,
            SlotValidator,
            PromptResolver,
            MetaPrIntakeService,
            WaveStartService,
            BoardService,
            TenantService,
            CheckpointEvidenceService,
            ForgeActionService,
            LearningIngestService,
            RunOrchestrator,
        )
        logger.info("DI container configured successfully")
    return _injector


async def _close_service(injector: Injector, service_type: Type[Any]) -> None:
    try:
        await injector.get(service_type).close()
    except Exception as e:
        logger.warning("Error closing service", service_type=service_type.__name__, error=str(e))


async def initialize_all_services() -> None:
    logger.info("Initializing all application services")
    injector = get_container()
    for service_type in _INFRA_SERVICE_TYPES:
        await injector.get(service_type).initialize()
    for service_type in _BUSINESS_SERVICE_TYPES:
        await injector.get(service_type).initialize()
    logger.info("All application services initialized successfully")


async def close_all_services() -> None:
    logger.info("Closing all application services")
    injector = get_container()
    for service_type in reversed(_BUSINESS_SERVICE_TYPES):
        await _close_service(injector, service_type)
    for service_type in reversed(_INFRA_SERVICE_TYPES):
        await _close_service(injector, service_type)
    logger.info("All application services closed")


def get_container() -> Injector:
    global _injector
    if _injector is None:
        raise RuntimeError("Call configure_container() first")
    return _injector


def reset_container() -> None:
    global _injector
    _injector = None


def provide_service(cls: Type[T]) -> T:
    if _injector is None:
        configure_container()
    return get_container().get(cls)
