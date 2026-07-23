"""Business services DI module for gateflow."""

from injector import Binder, Module, singleton

from src.business_services.handoff_reader import HandoffReader
from src.business_services.job_worker_service import JobWorkerService
from src.business_services.webhook_ingress_service import WebhookIngressService
from src.business_services.workflow_engine import WorkflowEngine


class BusinessServicesModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(WebhookIngressService, scope=singleton)
        binder.bind(JobWorkerService, scope=singleton)
        binder.bind(HandoffReader, scope=singleton)
        binder.bind(WorkflowEngine, scope=singleton)
