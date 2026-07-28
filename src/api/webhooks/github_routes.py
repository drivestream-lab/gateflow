"""GitHub App webhook ingress routes."""

import json
from typing import Any

from fastapi import APIRouter, Depends, Header, Request, Response, status

from src.business_services.webhook_ingress_service import (
    WebhookIngressService,
    get_webhook_ingress_service,
)
from src.configs.github_settings import GithubSettings
from src.logging import get_logger
from src.models.webhook_models import WebhookAcceptedResponse
from src.utils.github_webhook_signature import verify_github_webhook_signature

logger = get_logger()
router = APIRouter(tags=["Webhooks"])


@router.post(
    "/webhooks/github",
    response_model=WebhookAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(default="", alias="X-Hub-Signature-256"),
    x_github_delivery: str = Header(default="", alias="X-GitHub-Delivery"),
    x_github_event: str = Header(default="", alias="X-GitHub-Event"),
    service: WebhookIngressService = Depends(get_webhook_ingress_service),
) -> WebhookAcceptedResponse | Response:
    """Validate App signature, persist idempotency, enqueue job, return quickly."""
    body = await request.body()
    settings = GithubSettings.get_instance()
    secret = settings.webhook_secret.get_secret_value()
    signature_valid = verify_github_webhook_signature(secret, body, x_hub_signature_256)

    payload: dict[str, Any]
    if body:
        parsed = json.loads(body.decode("utf-8"))
        if not isinstance(parsed, dict):
            payload = {"_raw": parsed}
        else:
            payload = parsed
    else:
        payload = {}

    job_id = await service.enqueue_webhook_job(
        delivery_id=x_github_delivery,
        event_type=x_github_event or "unknown",
        payload=payload,
        signature_valid=signature_valid,
    )

    if job_id is None:
        logger.info(
            "Webhook accepted as idempotent duplicate",
            delivery_id=x_github_delivery,
            event_type=x_github_event,
        )
        return WebhookAcceptedResponse(
            accepted=True,
            duplicate=True,
            job_id=None,
        )

    return WebhookAcceptedResponse(
        accepted=True,
        duplicate=False,
        job_id=job_id,
    )
