"""Per-call GitHub PAT probe for tenant registration (INIT-GATEFLOW-012 REQ-06).

Uses a fresh httpx client with the *caller-submitted* credential — never the
ForgeClient / GithubTokenProvider singleton credential.
"""

from injector import inject

import httpx

from src.configs.github_settings import GithubSettings
from src.infra_services.base_infra_service import BaseInfraService
from src.logging import get_logger
from src.models.tenant_models import PatProbeResult

logger = get_logger()


class GithubPatProbe(BaseInfraService):
    """Eager read-access probe via GET /repos/{org}/{repo} (Q-2 default)."""

    @inject
    def __init__(self) -> None:
        super().__init__()
        self._settings = GithubSettings.get_instance()
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True
        logger.info("GithubPatProbe initialized")

    async def close(self) -> None:
        self._initialized = False

    async def health_check(self) -> bool:
        return self._initialized

    async def verify_read_access(self, credential: str, org: str, repo: str) -> PatProbeResult:
        """Return ok/reason; expected auth/not-found failures populate reason (no raise)."""
        if not credential.strip():
            return PatProbeResult(ok=False, reason="empty_credential")
        url = f"{self._settings.api_base_url.rstrip('/')}/repos/{org}/{repo}"
        headers = {
            "Authorization": f"Bearer {credential}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)
        except httpx.HTTPError as exc:
            logger.warning(
                "PAT probe transport error",
                org=org,
                repo=repo,
                error_type=type(exc).__name__,
            )
            return PatProbeResult(ok=False, reason=f"transport_error:{type(exc).__name__}")

        if response.status_code == 200:
            return PatProbeResult(ok=True, reason=None)
        if response.status_code == 401:
            return PatProbeResult(ok=False, reason="unauthorized")
        if response.status_code == 403:
            return PatProbeResult(ok=False, reason="forbidden")
        if response.status_code == 404:
            return PatProbeResult(ok=False, reason="not_found")
        return PatProbeResult(ok=False, reason=f"http_{response.status_code}")


def get_github_pat_probe() -> GithubPatProbe:
    from src.di.dependency_container import provide_service

    return provide_service(GithubPatProbe)
