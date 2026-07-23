"""Business services DI module for gateflow."""

from injector import Binder, Module, singleton

from src.business_services.webhook_ingress_service import WebhookIngressService


class BusinessServicesModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(WebhookIngressService, scope=singleton)
