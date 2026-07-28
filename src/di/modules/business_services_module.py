"""Business services DI module for gateflow."""

from injector import Binder, Module, singleton

from src.business_services.adapter_registry import AdapterRegistry
from src.business_services.board_service import BoardService
from src.business_services.handoff_reader import HandoffReader
from src.business_services.job_worker_service import JobWorkerService
from src.business_services.metrics_emitter import MetricsEmitter
from src.business_services.notifier import Notifier
from src.business_services.policy_engine import PolicyEngine
from src.business_services.prompt_resolver import PromptResolver
from src.business_services.run_orchestrator import RunOrchestrator
from src.business_services.slot_validator import SlotValidator
from src.business_services.trigger_router import TriggerRouter
from src.business_services.wave_start_service import WaveStartService
from src.business_services.webhook_ingress_service import WebhookIngressService
from src.business_services.workflow_engine import WorkflowEngine


class BusinessServicesModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(WebhookIngressService, scope=singleton)
        binder.bind(JobWorkerService, scope=singleton)
        binder.bind(HandoffReader, scope=singleton)
        binder.bind(WorkflowEngine, scope=singleton)
        binder.bind(TriggerRouter, scope=singleton)
        binder.bind(PolicyEngine, scope=singleton)
        binder.bind(Notifier, scope=singleton)
        binder.bind(MetricsEmitter, scope=singleton)
        binder.bind(AdapterRegistry, scope=singleton)
        binder.bind(SlotValidator, scope=singleton)
        binder.bind(PromptResolver, scope=singleton)
        binder.bind(WaveStartService, scope=singleton)
        binder.bind(BoardService, scope=singleton)
        binder.bind(RunOrchestrator, scope=singleton)
