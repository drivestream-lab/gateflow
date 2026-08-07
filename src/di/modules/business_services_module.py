"""Business services DI module for gateflow."""

from injector import Binder, Module, singleton

from src.business_services.adapter_registry import AdapterRegistry
from src.business_services.board_service import BoardService
from src.business_services.checkpoint_evidence_service import CheckpointEvidenceService
from src.business_services.closure_start_service import ClosureStartService
from src.business_services.closeout_readout_service import CloseoutReadoutService
from src.business_services.closure_preview_service import ClosurePreviewService
from src.business_services.completion_readout_service import CompletionReadoutService
from src.business_services.forge_action_service import ForgeActionService
from src.business_services.handoff_reader import HandoffReader
from src.business_services.implementation_readout_service import ImplementationReadoutService
from src.business_services.initiative_readout_service import InitiativeReadoutService
from src.business_services.job_worker_service import JobWorkerService
from src.business_services.learning_ingest_service import LearningIngestService
from src.business_services.merge_readout_service import MergeReadoutService
from src.business_services.meta_pr_intake import MetaPrIntakeService
from src.business_services.metrics_emitter import MetricsEmitter
from src.business_services.notifier import Notifier
from src.business_services.policy_engine import PolicyEngine
from src.business_services.prompt_resolver import PromptResolver
from src.business_services.run_orchestrator import RunOrchestrator
from src.business_services.slot_validator import SlotValidator
from src.business_services.spec_readout_service import SpecReadoutService
from src.business_services.trigger_router import TriggerRouter
from src.business_services.wave_map_service import WaveMapService
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
        binder.bind(MetaPrIntakeService, scope=singleton)
        binder.bind(WaveStartService, scope=singleton)
        binder.bind(ClosureStartService, scope=singleton)
        binder.bind(BoardService, scope=singleton)
        binder.bind(CheckpointEvidenceService, scope=singleton)
        binder.bind(InitiativeReadoutService, scope=singleton)
        binder.bind(WaveMapService, scope=singleton)
        binder.bind(SpecReadoutService, scope=singleton)
        binder.bind(ImplementationReadoutService, scope=singleton)
        binder.bind(CloseoutReadoutService, scope=singleton)
        binder.bind(MergeReadoutService, scope=singleton)
        binder.bind(CompletionReadoutService, scope=singleton)
        binder.bind(ClosurePreviewService, scope=singleton)
        binder.bind(ForgeActionService, scope=singleton)
        binder.bind(LearningIngestService, scope=singleton)
        binder.bind(RunOrchestrator, scope=singleton)
