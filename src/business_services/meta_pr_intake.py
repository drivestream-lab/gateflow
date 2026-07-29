"""MetaPrIntakeService — spec-lane meta PR accept-gate (ADR-010 / INIT-006 W4)."""

import re
from typing import Optional
from urllib.parse import urlparse

from injector import inject

from src.business_services.base_business_service import BaseBusinessService
from src.infra_services.forge_client import ForgeClient
from src.models.meta_pr_models import (
    GithubPullRequestDocument,
    MetaPrAcceptResult,
    MetaPrRef,
)

_GITHUB_PR_PATH_RE = re.compile(r"^/(?P<owner>[^/]+)/(?P<repo>[^/]+)/pull(?:s)?/(?P<number>\d+)/?$")
_INITIATIVE_RE = re.compile(r"\b(INIT-[A-Z0-9]+-\d+)\b")


class MetaPrIntakeService(BaseBusinessService):
    """Parse meta PR URLs, fetch via ForgeClient, enforce initiative consistency."""

    @inject
    def __init__(self, forge_client: ForgeClient) -> None:
        super().__init__()
        self._forge_client = forge_client

    def parse_url(self, url: str) -> MetaPrRef:
        """Parse a GitHub PR URL; fail closed on unexpected hosts/paths."""
        cleaned = url.strip()
        if not cleaned:
            raise ValueError("meta_pr_url is empty")
        parsed = urlparse(cleaned)
        if parsed.scheme not in {"http", "https"}:
            raise ValueError("meta_pr_url must be an http(s) URL")
        host = (parsed.hostname or "").lower()
        if host not in {"github.com", "www.github.com"} and not host.endswith(".github.com"):
            if "github" not in host:
                raise ValueError(f"meta_pr_url host not supported: {host or '(missing)'}")
        match = _GITHUB_PR_PATH_RE.match(parsed.path or "")
        if match is None:
            raise ValueError(
                "meta_pr_url must look like https://github.com/{owner}/{repo}/pull/{n}"
            )
        return MetaPrRef(
            owner=match.group("owner"),
            repo=match.group("repo"),
            pr_number=int(match.group("number")),
            source_url=cleaned,
        )

    def derive_initiative_id(self, pr: GithubPullRequestDocument) -> Optional[str]:
        """Best-effort initiative extraction from PR title/body/labels."""
        for text in (pr.title, pr.body or ""):
            found = _INITIATIVE_RE.search(text)
            if found:
                return found.group(1)
        for label in pr.labels:
            name = label.name
            if name.startswith("gateflow/initiative:"):
                return name.split(":", 1)[1].strip() or None
            found = _INITIATIVE_RE.search(name)
            if found:
                return found.group(1)
        return None

    async def accept(
        self,
        *,
        meta_pr_url: str,
        expected_initiative_id: str,
    ) -> MetaPrAcceptResult:
        """Fetch meta PR and enforce initiative consistency (ADR-010).

        Raises:
            ValueError: URL/shape/initiative fail closed (caller maps to 4xx).
            httpx.HTTPError: forge transport failure (caller maps to 503).
        """
        ref = self.parse_url(meta_pr_url)
        pr = await self._forge_client.get_pull_request(ref.owner, ref.repo, ref.pr_number)
        head_sha = pr.head.sha.strip()
        if not head_sha:
            raise ValueError(f"meta PR {ref.owner}/{ref.repo}#{ref.pr_number} missing head sha")

        derived = self.derive_initiative_id(pr)
        if derived is not None and derived != expected_initiative_id:
            raise ValueError(
                "meta PR initiative mismatch: "
                f"derived={derived!r} expected={expected_initiative_id!r}"
            )
        if derived is None:
            raise ValueError(
                "meta PR does not expose a derivable initiative id in title/body/labels"
            )

        self.logger.info(
            "Meta PR accept-gate passed",
            meta_owner=ref.owner,
            meta_repo=ref.repo,
            meta_pr_number=ref.pr_number,
            meta_head_sha=head_sha,
            initiative_id=derived,
        )
        return MetaPrAcceptResult(
            meta_pr_url=ref.source_url,
            meta_owner=ref.owner,
            meta_repo=ref.repo,
            meta_pr_number=ref.pr_number,
            meta_head_sha=head_sha,
            derived_initiative_id=derived,
        )


def get_meta_pr_intake_service() -> MetaPrIntakeService:
    from src.di.dependency_container import provide_service

    return provide_service(MetaPrIntakeService)
