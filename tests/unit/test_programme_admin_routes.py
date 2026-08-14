"""Unit tests for platform_admin programme routes (INIT-GATEFLOW-014 W1)."""

from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from src.api.v1 import programme_admin_routes as routes
from src.business_services.programme_service import get_programme_service
from src.common.auth.dependencies import require_role
from src.exceptions.app_exceptions import BaseAppException, ForbiddenError
from src.models.auth_models import AuthContext
from src.models.programme_catalogue_models import CatalogueCandidate
from src.models.programme_models import ProgrammeCreateResult, ProgrammeReadModel
from src.models.role_types import RoleType


@pytest.mark.asyncio
async def test_require_role_allows_platform_admin() -> None:
    dep = require_role(RoleType.PLATFORM_ADMIN)
    request = MagicMock()
    request.state.auth = AuthContext(user_id=uuid4(), role=RoleType.PLATFORM_ADMIN)
    assert (await dep(request)).role == RoleType.PLATFORM_ADMIN


@pytest.mark.asyncio
async def test_require_role_forbids_tenant_admin() -> None:
    dep = require_role(RoleType.PLATFORM_ADMIN)
    request = MagicMock()
    request.state.auth = AuthContext(
        user_id=uuid4(),
        role=RoleType.TENANT_ADMIN,
        tenant_id=uuid4(),
    )
    with pytest.raises(ForbiddenError):
        await dep(request)


def test_create_programme_route_platform_admin() -> None:
    app = FastAPI()

    @app.exception_handler(BaseAppException)
    async def _handler(_request: Request, exc: BaseAppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.code, "message": exc.message, "details": exc.details},
        )

    service = MagicMock()
    programme_id = uuid4()
    tenant_id = uuid4()
    from unittest.mock import AsyncMock

    service.validate_then_create = AsyncMock(
        return_value=ProgrammeCreateResult(
            programme_id=programme_id,
            tenant_id=tenant_id,
            repo_catalogue=[],
        )
    )

    app.include_router(routes.programme_router)
    app.dependency_overrides[get_programme_service] = lambda: service

    @app.middleware("http")
    async def inject_auth(request: Request, call_next):  # type: ignore[no-untyped-def]
        request.state.auth = AuthContext(user_id=uuid4(), role=RoleType.PLATFORM_ADMIN)
        return await call_next(request)

    client = TestClient(app)
    response = client.post(
        "/programmes",
        json={
            "name": "smoke",
            "meta_org": "o",
            "meta_repo": "r",
            "github_pat": "ghp_x",
        },
    )
    assert response.status_code == 200
    assert response.json()["programme_id"] == str(programme_id)


def test_get_programme_returns_repo_catalogue() -> None:
    app = FastAPI()

    @app.exception_handler(BaseAppException)
    async def _handler(_request: Request, exc: BaseAppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.code, "message": exc.message, "details": exc.details},
        )

    service = MagicMock()
    programme_id = uuid4()
    tenant_id = uuid4()
    from unittest.mock import AsyncMock

    service.get_programme = AsyncMock(
        return_value=ProgrammeReadModel(
            id=programme_id,
            name="smoke",
            tenant_id=tenant_id,
            workspace_root="/tmp/ws",
            meta_org="o",
            meta_repo="r",
            repo_catalogue=[],
        )
    )

    app.include_router(routes.programme_router)
    app.dependency_overrides[get_programme_service] = lambda: service

    @app.middleware("http")
    async def inject_auth(request: Request, call_next):  # type: ignore[no-untyped-def]
        request.state.auth = AuthContext(user_id=uuid4(), role=RoleType.PLATFORM_ADMIN)
        return await call_next(request)

    client = TestClient(app)
    response = client.get(f"/programmes/{programme_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(programme_id)
    assert body["repo_catalogue"] == []
    assert "pat" not in body
    assert "github_pat" not in body


def test_refresh_catalogue_route_platform_admin() -> None:
    app = FastAPI()

    @app.exception_handler(BaseAppException)
    async def _handler(_request: Request, exc: BaseAppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.code, "message": exc.message, "details": exc.details},
        )

    service = MagicMock()
    programme_id = uuid4()
    tenant_id = uuid4()
    from unittest.mock import AsyncMock

    service.refresh_catalogue = AsyncMock(
        return_value=ProgrammeReadModel(
            id=programme_id,
            name="smoke",
            tenant_id=tenant_id,
            workspace_root="/tmp/ws",
            meta_org="o",
            meta_repo="r",
            repo_catalogue=[
                CatalogueCandidate(
                    org="o",
                    repo="gateflow",
                    service_key="gateflow",
                    status="live",
                )
            ],
        )
    )

    app.include_router(routes.programme_router)
    app.dependency_overrides[get_programme_service] = lambda: service

    @app.middleware("http")
    async def inject_auth(request: Request, call_next):  # type: ignore[no-untyped-def]
        request.state.auth = AuthContext(user_id=uuid4(), role=RoleType.PLATFORM_ADMIN)
        return await call_next(request)

    client = TestClient(app)
    response = client.post(f"/programmes/{programme_id}/catalogue/refresh")
    assert response.status_code == 200
    body = response.json()
    assert body["repo_catalogue"][0]["repo"] == "gateflow"
    assert "pat" not in body
    assert "github_pat" not in body
    service.refresh_catalogue.assert_awaited_once()


def test_list_forbidden_for_tenant_admin() -> None:
    app = FastAPI()

    @app.exception_handler(BaseAppException)
    async def _handler(_request: Request, exc: BaseAppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.code, "message": exc.message, "details": exc.details},
        )

    app.include_router(routes.programme_router)

    @app.middleware("http")
    async def inject_auth(request: Request, call_next):  # type: ignore[no-untyped-def]
        request.state.auth = AuthContext(
            user_id=uuid4(),
            role=RoleType.TENANT_ADMIN,
            tenant_id=uuid4(),
        )
        return await call_next(request)

    client = TestClient(app)
    response = client.get("/programmes")
    assert response.status_code == 403
    assert response.json()["code"] == "FORBIDDEN"
