"""Webhook ingress business service — signature gate + idempotent enqueue."""

from typing import Optional
from uuid import UUID

from injector import inject

from src.business_services.base_business_service import BaseBusinessService
from src.database.postgres.repository.run_store_repository import (
    JobRepository,
    WebhookDeliveryRepository,
)
from src.exceptions.app_exceptions import ServiceUnavailableError, UnauthorizedError
from src.infra_services.postgres_service import PostgresService
from src.models.run_store_models import JobCreate, JobPayloadDocument, WebhookDeliveryCreate


class WebhookIngressService(BaseBusinessService):
    """Accept signed forge webhooks and enqueue async jobs (TDD §3.1)."""

    @inject
    def __init__(
        self,
        postgres_service: PostgresService,
        webhook_delivery_repository: WebhookDeliveryRepository,
        job_repository: JobRepository,
    ) -> None:
        super().__init__()
        self._postgres_service = postgres_service
        self._webhook_delivery_repository = webhook_delivery_repository
        self._job_repository = job_repository

    async def enqueue_webhook_job(
        self,
        delivery_id: str,
        event_type: str,
        payload: dict,
        signature_valid: bool,
    ) -> Optional[UUID]:
        """Enqueue a job for a validated delivery.

        Returns job id when a new job is created; None on idempotent duplicate.
        Raises UnauthorizedError when signature_valid is False.
        Raises ServiceUnavailableError when Postgres is unavailable.
        """
        if not signature_valid:
            raise UnauthorizedError(
                message="Invalid GitHub webhook signature",
                details={"delivery_id": delivery_id},
            )
        if not delivery_id:
            raise UnauthorizedError(message="Missing X-GitHub-Delivery header")

        try:
            async with self._postgres_service.transaction() as session:
                delivery, created = await self._webhook_delivery_repository.create_if_absent(
                    session,
                    WebhookDeliveryCreate(
                        delivery_id=delivery_id,
                        event_type=event_type,
                        payload=payload,
                    ),
                )
                if not created:
                    self.logger.info(
                        "Duplicate webhook delivery skipped",
                        delivery_id=delivery_id,
                        event_type=event_type,
                    )
                    return None

                job = await self._job_repository.enqueue(
                    session,
                    JobCreate(
                        delivery_id=delivery_id,
                        webhook_delivery_id=delivery.id,
                        payload=JobPayloadDocument.model_validate(
                            {
                                "delivery_id": delivery_id,
                                "event_type": event_type,
                                **payload,
                            }
                        ),
                    ),
                )
                self.logger.info(
                    "Webhook job enqueued",
                    delivery_id=delivery_id,
                    event_type=event_type,
                    job_id=str(job.id),
                )
                return job.id
        except UnauthorizedError:
            raise
        except Exception as exc:
            self.logger.exception(
                "Webhook enqueue failed",
                delivery_id=delivery_id,
                event_type=event_type,
            )
            raise ServiceUnavailableError(
                service_name="postgres",
                message="Unable to persist webhook delivery or enqueue job",
                details={"delivery_id": delivery_id, "error": str(exc)},
            ) from exc


def get_webhook_ingress_service() -> WebhookIngressService:
    from src.di.dependency_container import provide_service

    return provide_service(WebhookIngressService)
