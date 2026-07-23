"""API v1 — compose product routers here."""

from fastapi import APIRouter

from src.api.v1.metrics_routes import router as metrics_router
from src.api.v1.runs_routes import router as runs_router

api_router = APIRouter()
api_router.include_router(runs_router, tags=["Runs"])
api_router.include_router(metrics_router, tags=["Metrics"])
