"""API v1 — compose product routers here."""

from fastapi import APIRouter

from src.api.v1.board_routes import router as board_router
from src.api.v1.checkpoints_routes import router as checkpoints_router
from src.api.v1.forge_routes import router as forge_router
from src.api.v1.initiatives_routes import router as initiatives_router
from src.api.v1.metrics_routes import router as metrics_router
from src.api.v1.programme_admin_routes import (
    agent_catalogue_router,
    programme_router as programme_admin_router,
)
from src.api.v1.catalogue_connection_routes import router as catalogue_connection_router
from src.api.v1.runs_routes import router as runs_router
from src.api.v1.tenant_routes import router as tenant_router
from src.api.v1.waves_routes import router as waves_router

api_router = APIRouter()
api_router.include_router(waves_router, tags=["Waves"])
api_router.include_router(initiatives_router, tags=["Initiatives"])
api_router.include_router(runs_router, tags=["Runs"])
api_router.include_router(forge_router, tags=["Forge"])
api_router.include_router(metrics_router, tags=["Metrics"])
api_router.include_router(board_router, tags=["Board"])
api_router.include_router(checkpoints_router, tags=["Checkpoints"])
api_router.include_router(tenant_router, tags=["Tenants"])
api_router.include_router(catalogue_connection_router, tags=["CatalogueConnection"])
api_router.include_router(programme_admin_router)
api_router.include_router(agent_catalogue_router)
