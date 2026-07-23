"""Webhook routers package."""

from fastapi import APIRouter

from src.api.webhooks.github_routes import router as github_webhook_router

webhook_router = APIRouter()
webhook_router.include_router(github_webhook_router)
