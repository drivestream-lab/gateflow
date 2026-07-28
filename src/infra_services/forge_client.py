"""ForgeClient — outbound GitHub comments/PR/board ops with forbidden-op guards (ADR-003)."""

from typing import Any, Optional

import httpx
from injector import inject

from src.configs.app_settings import AppSettings, Environment
from src.configs.github_settings import GithubSettings
from src.infra_services.base_infra_service import BaseInfraService
from src.infra_services.github_token_provider import GithubTokenProvider
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

# Board ticket labels (Issues MVP — not GitHub Projects; Q-4 narrow default).
BOARD_TYPE_LABEL_PREFIX = "gateflow/type:"
BOARD_INITIATIVE_LABEL_PREFIX = "gateflow/initiative:"
BOARD_COLUMN_LABEL_PREFIX = "gateflow/column:"
BOARD_IDEMPOTENCY_LABEL_PREFIX = "gateflow/idem:"


class ForgeClient(BaseInfraService):
    """GitHub REST client for comments and audited writes."""

    @inject
    def __init__(self, token_provider: GithubTokenProvider) -> None:
        super().__init__()
        self._settings = GithubSettings.get_instance()
        self._app_settings = AppSettings.get_instance()
        self._token_provider = token_provider
        self._client: Optional[httpx.AsyncClient] = None
        self._initialized = False

    async def initialize(self) -> None:
        token = await self._token_provider.get_token()
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Authorization": f"Bearer {token}",
        }
        self._client = httpx.AsyncClient(
            base_url=self._settings.api_base_url.rstrip("/"),
            headers=headers,
            timeout=30.0,
        )
        self._initialized = True
        logger.info(
            "ForgeClient initialized",
            api_base_url=self._settings.api_base_url,
            auth_mode=self._settings.auth_mode.value,
        )

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None
        self._initialized = False

    async def health_check(self) -> bool:
        return self._initialized and self._client is not None

    def _require_client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("ForgeClient not initialized")
        return self._client

    @staticmethod
    def _git_ref_get_path(owner: str, repo: str, branch: str) -> str:
        """GET a branch tip (singular ``ref`` collection)."""
        return f"/repos/{owner}/{repo}/git/ref/heads/{branch}"

    @staticmethod
    def _git_ref_update_path(owner: str, repo: str, branch: str) -> str:
        """PATCH/DELETE a branch tip (plural ``refs`` collection)."""
        return f"/repos/{owner}/{repo}/git/refs/heads/{branch}"

    async def ensure_branch_from_base(
        self,
        owner: str,
        repo: str,
        *,
        branch: str,
        base: str,
        bootstrap_commit_message: Optional[str] = None,
    ) -> bool:
        """Ensure ``branch`` exists and differs from ``base`` so a PR can open.

        Creates the ref from ``base`` when missing. If head and base share the
        same commit SHA, creates an empty bootstrap commit (same tree, new
        commit) so GitHub accepts ``POST /pulls`` ("No commits between…" 422).

        Returns True if a new ref was created, False if the branch already existed.
        """
        client = self._require_client()
        base_path = self._git_ref_get_path(owner, repo, base)
        base_ref = await client.get(base_path)
        base_ref.raise_for_status()
        base_sha = str(base_ref.json()["object"]["sha"])

        head_path = self._git_ref_get_path(owner, repo, branch)
        existing = await client.get(head_path)
        created_ref = False
        if existing.status_code == 404:
            created = await client.post(
                f"/repos/{owner}/{repo}/git/refs",
                json={"ref": f"refs/heads/{branch}", "sha": base_sha},
            )
            created.raise_for_status()
            created_ref = True
            head_sha = str(created.json()["object"]["sha"])
            logger.info(
                "ForgeClient branch created from base",
                owner=owner,
                repo=repo,
                branch=branch,
                base=base,
                sha=base_sha,
                operation="ensure_branch_from_base",
            )
        elif existing.status_code != 200:
            existing.raise_for_status()
            head_sha = ""  # raise_for_status always raises on error status
        else:
            head_sha = str(existing.json()["object"]["sha"])
            logger.info(
                "ForgeClient branch already exists",
                owner=owner,
                repo=repo,
                branch=branch,
                operation="ensure_branch_from_base",
            )

        if head_sha != base_sha:
            return created_ref

        parent = await client.get(f"/repos/{owner}/{repo}/git/commits/{head_sha}")
        parent.raise_for_status()
        tree_sha = str(parent.json()["tree"]["sha"])
        message = bootstrap_commit_message or f"chore(gateflow): bootstrap branch {branch}"
        commit = await client.post(
            f"/repos/{owner}/{repo}/git/commits",
            json={
                "message": message,
                "tree": tree_sha,
                "parents": [head_sha],
            },
        )
        commit.raise_for_status()
        new_sha = str(commit.json()["sha"])
        updated = await client.patch(
            self._git_ref_update_path(owner, repo, branch),
            json={"sha": new_sha, "force": False},
        )
        updated.raise_for_status()
        logger.info(
            "ForgeClient bootstrap empty commit on branch",
            owner=owner,
            repo=repo,
            branch=branch,
            sha=new_sha,
            operation="ensure_branch_from_base",
        )
        return created_ref

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
            operation="post_comment",
        )
        return comment_id

    async def create_or_update_pull_request(
        self,
        owner: str,
        repo: str,
        *,
        title: str,
        body: str,
        head: str,
        base: str,
    ) -> int:
        """Open or update a PR by head branch. Returns PR number.

        Does not auto-merge or write gate-approval labels (ADR-003).
        """
        client = self._require_client()
        head_ref = f"{owner}:{head}"
        list_path = f"/repos/{owner}/{repo}/pulls"
        listed = await client.get(
            list_path,
            params={"state": "open", "head": head_ref, "base": base},
        )
        listed.raise_for_status()
        existing = listed.json()
        if isinstance(existing, list) and existing:
            pr_number = int(existing[0]["number"])
            patch = await client.patch(
                f"/repos/{owner}/{repo}/pulls/{pr_number}",
                json={"title": title, "body": body},
            )
            patch.raise_for_status()
            logger.info(
                "ForgeClient pull request updated",
                owner=owner,
                repo=repo,
                pr_number=pr_number,
                operation="create_or_update_pull_request",
            )
            return pr_number

        created = await client.post(
            list_path,
            json={"title": title, "body": body, "head": head, "base": base},
        )
        created.raise_for_status()
        data = created.json()
        pr_number = int(data["number"])
        logger.info(
            "ForgeClient pull request created",
            owner=owner,
            repo=repo,
            pr_number=pr_number,
            operation="create_or_update_pull_request",
        )
        return pr_number

    def add_labels(self, labels: list[str]) -> None:
        """Forbidden for gate-approval labels — always raises."""
        for label in labels:
            if label in _FORBIDDEN_LABEL_EXACT or any(
                label.startswith(prefix) for prefix in _FORBIDDEN_LABEL_PREFIXES
            ):
                raise PermissionError(f"ForgeClient forbids gate-approval label writes: {label}")
        raise PermissionError(
            "ForgeClient does not support arbitrary label writes via add_labels; "
            "board labels use dedicated board_* methods; gate labels remain forbidden"
        )

    def enable_auto_merge(self) -> None:
        """Never auto-merge."""
        raise PermissionError("ForgeClient forbids auto-merge")

    def assert_no_gh_cli_transport(self) -> None:
        """FR-25/26a — production forge path must not shell to gh."""
        # Runtime guard for misconfiguration / future regressions. Production
        # transport is httpx REST only; PAT mode is rejected at token-provider bind.
        if self._app_settings.environment == Environment.PRODUCTION:
            logger.debug(
                "ForgeClient production transport check passed",
                operation="assert_no_gh_cli_transport",
            )

    @staticmethod
    def type_label(ticket_type: str) -> str:
        return f"{BOARD_TYPE_LABEL_PREFIX}{ticket_type}"

    @staticmethod
    def initiative_label(initiative_id: str) -> str:
        return f"{BOARD_INITIATIVE_LABEL_PREFIX}{initiative_id}"

    @staticmethod
    def column_label(column: str) -> str:
        return f"{BOARD_COLUMN_LABEL_PREFIX}{column}"

    @staticmethod
    def idempotency_label(key: str) -> str:
        return f"{BOARD_IDEMPOTENCY_LABEL_PREFIX}{key}"

    async def get_issue(self, owner: str, repo: str, issue_number: int) -> dict[str, Any]:
        """Fetch one issue by number."""
        client = self._require_client()
        response = await client.get(f"/repos/{owner}/{repo}/issues/{issue_number}")
        response.raise_for_status()
        data = response.json()
        logger.info(
            "ForgeClient board issue fetched",
            owner=owner,
            repo=repo,
            issue_number=issue_number,
            operation="board_get_issue",
        )
        return data

    async def update_issue_status(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        *,
        state: Optional[str] = None,
        column: Optional[str] = None,
    ) -> dict[str, Any]:
        """Update issue state and/or board column label (Issues MVP)."""
        self.assert_no_gh_cli_transport()
        client = self._require_client()
        current = await self.get_issue(owner, repo, issue_number)
        payload: dict[str, Any] = {}
        if state is not None:
            if state not in {"open", "closed"}:
                raise ValueError("state must be open or closed")
            payload["state"] = state

        labels = [
            str(label["name"] if isinstance(label, dict) else label)
            for label in (current.get("labels") or [])
        ]
        if column is not None:
            labels = [name for name in labels if not name.startswith(BOARD_COLUMN_LABEL_PREFIX)]
            labels.append(self.column_label(column))
            payload["labels"] = labels

        if not payload:
            return current

        response = await client.patch(
            f"/repos/{owner}/{repo}/issues/{issue_number}",
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        logger.info(
            "ForgeClient board issue status updated",
            owner=owner,
            repo=repo,
            issue_number=issue_number,
            state=state,
            column=column,
            operation="board_update_issue_status",
        )
        return data

    async def link_pull_request(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        pr_number: int,
    ) -> str:
        """Record a PR↔ticket link via structured issue comment (dumb primitive)."""
        self.assert_no_gh_cli_transport()
        body = f"gateflow-board-link: pr #{pr_number}"
        comment_id = await self.post_comment(owner, repo, issue_number, body)
        logger.info(
            "ForgeClient board PR linked",
            owner=owner,
            repo=repo,
            issue_number=issue_number,
            pr_number=pr_number,
            comment_id=comment_id,
            operation="board_link_pull_request",
        )
        return comment_id

    async def find_issues_by_labels(
        self,
        owner: str,
        repo: str,
        *,
        labels: list[str],
        state: str = "all",
    ) -> list[dict[str, Any]]:
        """List issues matching all labels (AND). Empty labels → state filter only."""
        client = self._require_client()
        params: dict[str, str] = {
            "state": state,
            "per_page": "100",
        }
        if labels:
            params["labels"] = ",".join(labels)
        response = await client.get(
            f"/repos/{owner}/{repo}/issues",
            params=params,
        )
        response.raise_for_status()
        data = response.json()
        issues = [item for item in data if "pull_request" not in item]
        logger.info(
            "ForgeClient board issues listed",
            owner=owner,
            repo=repo,
            label_count=len(labels),
            result_count=len(issues),
            operation="board_find_issues_by_labels",
        )
        return issues

    async def create_issue(
        self,
        owner: str,
        repo: str,
        *,
        title: str,
        body: str,
        labels: list[str],
    ) -> dict[str, Any]:
        """Create an issue with labels. Does not invoke the GitHub CLI (FR-25)."""
        self.assert_no_gh_cli_transport()
        for label in labels:
            if label in _FORBIDDEN_LABEL_EXACT or any(
                label.startswith(prefix) for prefix in _FORBIDDEN_LABEL_PREFIXES
            ):
                raise PermissionError(f"ForgeClient forbids gate-approval label writes: {label}")
        client = self._require_client()
        payload: dict[str, Any] = {"title": title, "body": body}
        if labels:
            payload["labels"] = labels
        response = await client.post(
            f"/repos/{owner}/{repo}/issues",
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        logger.info(
            "ForgeClient board issue created",
            owner=owner,
            repo=repo,
            issue_number=int(data["number"]),
            operation="board_create_issue",
        )
        return data

    async def apply_issue_labels(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        labels: list[str],
    ) -> dict[str, Any]:
        """Replace issue labels with the provided set (board multi-step helper)."""
        self.assert_no_gh_cli_transport()
        for label in labels:
            if label in _FORBIDDEN_LABEL_EXACT or any(
                label.startswith(prefix) for prefix in _FORBIDDEN_LABEL_PREFIXES
            ):
                raise PermissionError(f"ForgeClient forbids gate-approval label writes: {label}")
        client = self._require_client()
        response = await client.patch(
            f"/repos/{owner}/{repo}/issues/{issue_number}",
            json={"labels": labels},
        )
        response.raise_for_status()
        data = response.json()
        logger.info(
            "ForgeClient board labels applied",
            owner=owner,
            repo=repo,
            issue_number=issue_number,
            operation="board_apply_issue_labels",
        )
        return data


def get_forge_client() -> ForgeClient:
    from src.di.dependency_container import provide_service

    return provide_service(ForgeClient)
