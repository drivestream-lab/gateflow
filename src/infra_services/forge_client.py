"""ForgeClient — outbound GitHub comments with forbidden-op guards (ADR-003)."""

from typing import Optional

import httpx
from injector import inject

from src.configs.app_settings import AppSettings, Environment
from src.configs.github_settings import GithubSettings
from src.infra_services.base_infra_service import BaseInfraService
from src.logging import get_logger

logger = get_logger()

# Product invariant — never write these labels / never auto-merge.
_FORBIDDEN_LABEL_PREFIXES = (
    "spec-lgtm",
    "impact-map-lgtm",
    "gate:",
)
_FORBIDDEN_LABEL_EXACT = frozenset(
    {
        "spec-lgtm",
        "spec-blocked",
        "impact-map-lgtm",
    }
)


class ForgeClient(BaseInfraService):
    """GitHub REST client for comments and audited writes."""

    @inject
    def __init__(self) -> None:
        super().__init__()
        self._settings = GithubSettings.get_instance()
        self._app_settings = AppSettings.get_instance()
        self._client: Optional[httpx.AsyncClient] = None
        self._initialized = False

    async def initialize(self) -> None:
        token = self._resolve_token()
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self._client = httpx.AsyncClient(
            base_url=self._settings.api_base_url.rstrip("/"),
            headers=headers,
            timeout=30.0,
        )
        self._initialized = True
        logger.info("ForgeClient initialized", api_base_url=self._settings.api_base_url)

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None
        self._initialized = False

    async def health_check(self) -> bool:
        return self._initialized and self._client is not None

    def _resolve_token(self) -> Optional[str]:
        """App installation token preferred; scoped PAT only when non-prod configured."""
        pat = self._settings.personal_access_token
        if pat is not None and self._app_settings.environment != Environment.PRODUCTION:
            return pat.get_secret_value()
        # Production App token minting deferred — caller must configure PAT for non-prod W0.
        if pat is not None:
            raise RuntimeError(
                "GITHUB_PERSONAL_ACCESS_TOKEN is not allowed in production (ADR-003)"
            )
        return None

    def _require_client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("ForgeClient not initialized")
        return self._client

    async def post_comment(self, owner: str, repo: str, issue_number: int, body: str) -> str:
        """Post a PR/issue comment. Returns comment id as string."""
        client = self._require_client()
        path = f"/repos/{owner}/{repo}/issues/{issue_number}/comments"
        response = await client.post(path, json={"body": body})
        response.raise_for_status()
        data = response.json()
        comment_id = str(data.get("id", ""))
        logger.info(
            "ForgeClient comment posted",
            owner=owner,
            repo=repo,
            issue_number=issue_number,
            comment_id=comment_id,
        )
        return comment_id

    def add_labels(self, labels: list[str]) -> None:
        """Forbidden for gate-approval labels — always raises."""
        for label in labels:
            if label in _FORBIDDEN_LABEL_EXACT or any(
                label.startswith(prefix) for prefix in _FORBIDDEN_LABEL_PREFIXES
            ):
                raise PermissionError(f"ForgeClient forbids gate-approval label writes: {label}")
        raise PermissionError(
            "ForgeClient W0 does not support label writes except programme run-status "
            "(not implemented in W0); gate labels remain forbidden"
        )

    def enable_auto_merge(self) -> None:
        """Never auto-merge."""
        raise PermissionError("ForgeClient forbids auto-merge")


def get_forge_client() -> ForgeClient:
    from src.di.dependency_container import provide_service

    return provide_service(ForgeClient)
