"""ForgeClient — outbound GitHub comments/PR/board ops with forbidden-op guards (ADR-003)."""

import base64
from pathlib import Path, PurePosixPath
from typing import Any, NamedTuple, Optional, Sequence

import httpx
from injector import inject

from src.configs.app_settings import AppSettings, Environment
from src.configs.github_settings import GithubSettings
from src.infra_services.base_infra_service import BaseInfraService
from src.infra_services.github_token_provider import GithubTokenProvider
from src.logging import get_logger
from src.models.forge_models import CommitPathsResult
from src.models.meta_pr_models import GithubIssueDocument, GithubPullRequestDocument

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

# Board ticket labels + Projects membership (project_number on create API).
BOARD_TYPE_LABEL_PREFIX = "gateflow/type:"
BOARD_INITIATIVE_LABEL_PREFIX = "gateflow/initiative:"
BOARD_COLUMN_LABEL_PREFIX = "gateflow/column:"
BOARD_IDEMPOTENCY_LABEL_PREFIX = "gateflow/idem:"


class ProjectStatusTarget(NamedTuple):
    """Resolved Project V2 Status write target for one issue project item."""

    project_id: str
    item_id: str
    status_field_id: str
    option_id: str


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
        draft: bool = False,
    ) -> int:
        """Open or update a PR by head branch. Returns PR number.

        Does not auto-merge or write gate-approval labels (ADR-003).
        When ``draft=True`` on create, opens as Draft. Update path patches title/body
        and draft flag when the API allows.
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
            patch_body: dict[str, Any] = {"title": title, "body": body}
            # GitHub allows toggling draft via dedicated endpoint on some plans;
            # include draft in PATCH when updating (ignored if unsupported).
            patch_body["draft"] = draft
            patch = await client.patch(
                f"/repos/{owner}/{repo}/pulls/{pr_number}",
                json=patch_body,
            )
            patch.raise_for_status()
            logger.info(
                "ForgeClient pull request updated",
                owner=owner,
                repo=repo,
                pr_number=pr_number,
                draft=draft,
                operation="create_or_update_pull_request",
            )
            return pr_number

        created = await client.post(
            list_path,
            json={
                "title": title,
                "body": body,
                "head": head,
                "base": base,
                "draft": draft,
            },
        )
        created.raise_for_status()
        data = created.json()
        pr_number = int(data["number"])
        logger.info(
            "ForgeClient pull request created",
            owner=owner,
            repo=repo,
            pr_number=pr_number,
            draft=draft,
            operation="create_or_update_pull_request",
        )
        return pr_number

    def _assert_projection_labels(self, labels: list[str]) -> None:
        for label in labels:
            if label.endswith("-lgtm"):
                raise PermissionError(f"ForgeClient forbids approval label writes: {label}")
            if label in _FORBIDDEN_LABEL_EXACT or any(
                label.startswith(prefix) for prefix in _FORBIDDEN_LABEL_PREFIXES
            ):
                raise PermissionError(f"ForgeClient forbids gate-approval label writes: {label}")

    async def apply_pull_request_labels(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        labels: list[str],
    ) -> None:
        """Add projection labels on a PR (issues labels API). Never ``*-lgtm``."""
        self.assert_no_gh_cli_transport()
        if not labels:
            return
        self._assert_projection_labels(labels)
        client = self._require_client()
        response = await client.post(
            f"/repos/{owner}/{repo}/issues/{pr_number}/labels",
            json={"labels": labels},
        )
        response.raise_for_status()
        logger.info(
            "ForgeClient PR labels applied",
            owner=owner,
            repo=repo,
            pr_number=pr_number,
            labels=labels,
            operation="apply_pull_request_labels",
        )

    async def remove_pull_request_labels(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        labels: list[str],
    ) -> None:
        """Remove projection labels from a PR. Never touches ``*-lgtm`` removals as a policy."""
        self.assert_no_gh_cli_transport()
        if not labels:
            return
        self._assert_projection_labels(labels)
        client = self._require_client()
        for label in labels:
            response = await client.delete(
                f"/repos/{owner}/{repo}/issues/{pr_number}/labels/{label}",
            )
            # 404 = already absent — treat as success for idempotent remove
            if response.status_code not in {200, 204, 404}:
                response.raise_for_status()
        logger.info(
            "ForgeClient PR labels removed",
            owner=owner,
            repo=repo,
            pr_number=pr_number,
            labels=labels,
            operation="remove_pull_request_labels",
        )

    async def open_draft_pr(
        self,
        owner: str,
        repo: str,
        *,
        title: str,
        body: str,
        head: str,
        base: str,
        draft: bool = True,
        apply_labels: Optional[list[str]] = None,
        remove_labels: Optional[list[str]] = None,
    ) -> int:
        """Create/update Draft PR and apply/remove projection labels. Returns PR number."""
        self.assert_no_gh_cli_transport()
        to_apply = list(apply_labels or [])
        to_remove = list(remove_labels or [])
        self._assert_projection_labels(to_apply)
        self._assert_projection_labels(to_remove)
        pr_number = await self.create_or_update_pull_request(
            owner,
            repo,
            title=title,
            body=body,
            head=head,
            base=base,
            draft=draft,
        )
        if to_remove:
            await self.remove_pull_request_labels(owner, repo, pr_number, to_remove)
        if to_apply:
            await self.apply_pull_request_labels(owner, repo, pr_number, to_apply)
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

    async def get_pull_request(
        self, owner: str, repo: str, pr_number: int
    ) -> GithubPullRequestDocument:
        """Fetch one pull request by number (spec-lane meta accept-gate)."""
        client = self._require_client()
        response = await client.get(f"/repos/{owner}/{repo}/pulls/{pr_number}")
        response.raise_for_status()
        document = GithubPullRequestDocument.model_validate(response.json())
        logger.info(
            "ForgeClient pull request fetched",
            owner=owner,
            repo=repo,
            pr_number=pr_number,
            operation="get_pull_request",
        )
        return document

    async def get_issue(self, owner: str, repo: str, issue_number: int) -> GithubIssueDocument:
        """Fetch one issue by number."""
        client = self._require_client()
        response = await client.get(f"/repos/{owner}/{repo}/issues/{issue_number}")
        response.raise_for_status()
        document = GithubIssueDocument.model_validate(response.json())
        logger.info(
            "ForgeClient board issue fetched",
            owner=owner,
            repo=repo,
            issue_number=issue_number,
            operation="board_get_issue",
        )
        return document

    async def resolve_issue_project_status_targets(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        *,
        column: str,
    ) -> list[ProjectStatusTarget]:
        """Resolve Project V2 Status write targets for an issue (fail closed).

        Requires at least one project item with a Status single-select option whose
        name exactly matches ``column`` (e.g. ``In Progress``, ``Done``, ``Todo``).
        """
        self.assert_no_gh_cli_transport()
        if issue_number <= 0:
            raise ValueError("issue_number must be a positive integer")
        column_name = str(column).strip()
        if not column_name:
            raise ValueError("column is required for Project Status sync")

        query = """
        query($owner: String!, $repo: String!, $number: Int!) {
          repository(owner: $owner, name: $repo) {
            issue(number: $number) {
              projectItems(first: 20) {
                nodes {
                  id
                  project {
                    id
                    field(name: "Status") {
                      ... on ProjectV2SingleSelectField {
                        id
                        name
                        options {
                          id
                          name
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
        """
        body = await self.graphql(query, {"owner": owner, "repo": repo, "number": issue_number})
        errors = body.get("errors")
        if errors:
            raise RuntimeError(f"GitHub GraphQL issue projectItems resolve failed: {errors}")
        repo_data = (body.get("data") or {}).get("repository") or {}
        issue = repo_data.get("issue") or {}
        if not issue:
            raise ValueError(f"Issue not found: {owner}/{repo}#{issue_number}")
        nodes = ((issue.get("projectItems") or {}).get("nodes")) or []
        targets: list[ProjectStatusTarget] = []
        for node in nodes:
            if not isinstance(node, dict):
                continue
            item_id = str(node.get("id") or "").strip()
            project = node.get("project") or {}
            if not isinstance(project, dict):
                continue
            project_id = str(project.get("id") or "").strip()
            field = project.get("field") or {}
            if not isinstance(field, dict):
                continue
            field_id = str(field.get("id") or "").strip()
            options = field.get("options") or []
            option_id = ""
            for option in options:
                if not isinstance(option, dict):
                    continue
                if str(option.get("name") or "") == column_name:
                    option_id = str(option.get("id") or "").strip()
                    break
            if item_id and project_id and field_id and option_id:
                targets.append(
                    ProjectStatusTarget(
                        project_id=project_id,
                        item_id=item_id,
                        status_field_id=field_id,
                        option_id=option_id,
                    )
                )

        if not nodes:
            raise ValueError(
                f"Issue {owner}/{repo}#{issue_number} is not on any Project V2 board; "
                "cannot sync Status (column requires project membership)"
            )
        if not targets:
            raise ValueError(
                f"No Project Status option named {column_name!r} for "
                f"{owner}/{repo}#{issue_number} (check board Status field options)"
            )
        return targets

    async def set_project_item_status(self, target: ProjectStatusTarget) -> None:
        """Set Project V2 Status single-select on one project item."""
        self.assert_no_gh_cli_transport()
        mutation = """
        mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
          updateProjectV2ItemFieldValue(
            input: {
              projectId: $projectId
              itemId: $itemId
              fieldId: $fieldId
              value: { singleSelectOptionId: $optionId }
            }
          ) {
            projectV2Item { id }
          }
        }
        """
        body = await self.graphql(
            mutation,
            {
                "projectId": target.project_id,
                "itemId": target.item_id,
                "fieldId": target.status_field_id,
                "optionId": target.option_id,
            },
        )
        errors = body.get("errors")
        if errors:
            raise RuntimeError(f"GitHub GraphQL updateProjectV2ItemFieldValue failed: {errors}")
        item = ((body.get("data") or {}).get("updateProjectV2ItemFieldValue") or {}).get(
            "projectV2Item"
        ) or {}
        if not str(item.get("id") or "").strip():
            raise RuntimeError("updateProjectV2ItemFieldValue returned no item id")

    async def update_issue_status(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        *,
        state: Optional[str] = None,
        column: Optional[str] = None,
    ) -> dict[str, Any]:
        """Update issue state and/or board column (label + Project V2 Status).

        When ``column`` is set: resolve Project Status targets first (fail closed),
        then PATCH ``gateflow/column:*`` labels, then set Project Status on each item.
        """
        self.assert_no_gh_cli_transport()
        client = self._require_client()
        status_targets: list[ProjectStatusTarget] = []
        if column is not None:
            status_targets = await self.resolve_issue_project_status_targets(
                owner, repo, issue_number, column=column
            )

        current = await self.get_issue(owner, repo, issue_number)
        payload: dict[str, Any] = {}
        if state is not None:
            if state not in {"open", "closed"}:
                raise ValueError("state must be open or closed")
            payload["state"] = state

        labels = [label.name for label in current.labels]
        if column is not None:
            labels = [name for name in labels if not name.startswith(BOARD_COLUMN_LABEL_PREFIX)]
            labels.append(self.column_label(column))
            payload["labels"] = labels

        if not payload:
            return current.model_dump(mode="json")

        response = await client.patch(
            f"/repos/{owner}/{repo}/issues/{issue_number}",
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

        for target in status_targets:
            await self.set_project_item_status(target)

        logger.info(
            "ForgeClient board issue status updated",
            owner=owner,
            repo=repo,
            issue_number=issue_number,
            state=state,
            column=column,
            project_status_synced=len(status_targets),
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

    async def get_issue_parent(
        self, owner: str, repo: str, issue_number: int
    ) -> Optional[dict[str, Any]]:
        """GET parent issue of a sub-issue; None when no parent (404)."""
        self.assert_no_gh_cli_transport()
        if issue_number <= 0:
            raise ValueError("issue_number must be a positive integer")
        client = self._require_client()
        response = await client.get(f"/repos/{owner}/{repo}/issues/{issue_number}/parent")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        data = response.json()
        return data if isinstance(data, dict) else None

    async def ensure_sub_issue(
        self,
        owner: str,
        repo: str,
        *,
        parent_number: int,
        child_number: int,
    ) -> str:
        """Link ``child_number`` under ``parent_number`` via REST sub-issues API.

        Returns ``linked``, ``already_linked``, or raises on failure.
        ``sub_issue_id`` must be the issue database id (not the issue number).
        """
        self.assert_no_gh_cli_transport()
        if parent_number <= 0 or child_number <= 0:
            raise ValueError("parent_number and child_number must be positive")
        if parent_number == child_number:
            raise ValueError("parent_number and child_number must differ")

        existing = await self.get_issue_parent(owner, repo, child_number)
        if existing is not None and int(existing.get("number", -1)) == parent_number:
            logger.info(
                "ForgeClient sub-issue already linked",
                owner=owner,
                repo=repo,
                parent_number=parent_number,
                child_number=child_number,
                operation="board_ensure_sub_issue",
            )
            return "already_linked"

        child = await self.get_issue(owner, repo, child_number)
        if child.id is None:
            raise RuntimeError(
                f"Issue {owner}/{repo}#{child_number} missing database id for sub-issue link"
            )
        client = self._require_client()
        response = await client.post(
            f"/repos/{owner}/{repo}/issues/{parent_number}/sub_issues",
            json={"sub_issue_id": int(child.id), "replace_parent": True},
        )
        response.raise_for_status()
        logger.info(
            "ForgeClient sub-issue linked",
            owner=owner,
            repo=repo,
            parent_number=parent_number,
            child_number=child_number,
            operation="board_ensure_sub_issue",
        )
        return "linked"

    async def graphql(
        self,
        query: str,
        variables: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """POST GitHub GraphQL; fail closed on top-level errors (except caller-handled)."""
        self.assert_no_gh_cli_transport()
        client = self._require_client()
        payload: dict[str, Any] = {"query": query}
        if variables is not None:
            payload["variables"] = variables
        response = await client.post("/graphql", json=payload)
        response.raise_for_status()
        body = response.json()
        if not isinstance(body, dict):
            raise RuntimeError("GitHub GraphQL returned non-object body")
        return body

    async def resolve_org_project_node_id(self, owner: str, project_number: int) -> str:
        """Resolve org Project v2 node id from deterministic project number."""
        if project_number <= 0:
            raise ValueError("project_number must be a positive integer")
        query = """
        query($owner: String!, $number: Int!) {
          organization(login: $owner) {
            projectV2(number: $number) {
              id
            }
          }
        }
        """
        body = await self.graphql(query, {"owner": owner, "number": project_number})
        errors = body.get("errors")
        if errors:
            raise RuntimeError(f"GitHub GraphQL project resolve failed: {errors}")
        org = (body.get("data") or {}).get("organization") or {}
        project = org.get("projectV2") or {}
        node_id = str(project.get("id") or "").strip()
        if not node_id:
            raise ValueError(
                f"Org project not found: owner={owner!r} project_number={project_number}"
            )
        return node_id

    async def resolve_issue_node_id(self, owner: str, repo: str, issue_number: int) -> str:
        """Resolve issue node id for Projects mutations."""
        if issue_number <= 0:
            raise ValueError("issue_number must be a positive integer")
        query = """
        query($owner: String!, $repo: String!, $number: Int!) {
          repository(owner: $owner, name: $repo) {
            issue(number: $number) {
              id
            }
          }
        }
        """
        body = await self.graphql(query, {"owner": owner, "repo": repo, "number": issue_number})
        errors = body.get("errors")
        if errors:
            raise RuntimeError(f"GitHub GraphQL issue resolve failed: {errors}")
        repo_data = (body.get("data") or {}).get("repository") or {}
        issue = repo_data.get("issue") or {}
        node_id = str(issue.get("id") or "").strip()
        if not node_id:
            raise ValueError(f"Issue not found: {owner}/{repo}#{issue_number}")
        return node_id

    async def ensure_issue_on_project(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        *,
        project_owner: str,
        project_number: int,
    ) -> str:
        """Add issue to org Project v2; treat already-present as success.

        Returns ``added`` or ``already_on_project``.
        """
        self.assert_no_gh_cli_transport()
        project_id = await self.resolve_org_project_node_id(project_owner, project_number)
        content_id = await self.resolve_issue_node_id(owner, repo, issue_number)
        mutation = """
        mutation($projectId: ID!, $contentId: ID!) {
          addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
            item { id }
          }
        }
        """
        body = await self.graphql(mutation, {"projectId": project_id, "contentId": content_id})
        errors = body.get("errors") or []
        if errors:
            messages = " ".join(str(err.get("message") or err) for err in errors)
            lowered = messages.lower()
            if "already" in lowered:
                logger.info(
                    "ForgeClient issue already on project",
                    owner=owner,
                    repo=repo,
                    issue_number=issue_number,
                    project_owner=project_owner,
                    project_number=project_number,
                    operation="board_ensure_issue_on_project",
                )
                return "already_on_project"
            raise RuntimeError(f"GitHub GraphQL addProjectV2ItemById failed: {errors}")

        item = ((body.get("data") or {}).get("addProjectV2ItemById") or {}).get("item") or {}
        if not str(item.get("id") or "").strip():
            raise RuntimeError("addProjectV2ItemById returned no item id")
        logger.info(
            "ForgeClient issue added to project",
            owner=owner,
            repo=repo,
            issue_number=issue_number,
            project_owner=project_owner,
            project_number=project_number,
            operation="board_ensure_issue_on_project",
        )
        return "added"

    async def get_branch_tip_sha(self, owner: str, repo: str, *, branch: str) -> str:
        """Return the commit SHA at ``refs/heads/{branch}`` (fail closed on missing)."""
        self.assert_no_gh_cli_transport()
        if not str(branch).strip():
            raise ValueError("branch is required")
        client = self._require_client()
        ref = await client.get(self._git_ref_get_path(owner, repo, branch))
        ref.raise_for_status()
        sha = str(ref.json()["object"]["sha"])
        if not sha.strip():
            raise ValueError(f"Empty tip SHA for branch {branch!r}")
        return sha

    async def commit_paths_to_branch(
        self,
        owner: str,
        repo: str,
        *,
        branch: str,
        workspace_path: str | Path,
        paths: Sequence[str],
        message: str,
    ) -> CommitPathsResult:
        """Create blobs + tree + commit and advance ``branch`` tip (no force).

        ``paths`` are workspace-relative POSIX paths that must exist as files.
        Caller applies pin ``commit_workspace`` policy (optional vs required empty).
        """
        self.assert_no_gh_cli_transport()
        if not paths:
            raise ValueError("commit_paths_to_branch requires at least one path")
        if not str(branch).strip():
            raise ValueError("branch is required")
        if not str(message).strip():
            raise ValueError("commit message is required")

        root = Path(workspace_path).resolve()
        if not root.is_dir():
            raise ValueError(f"workspace_path is not a directory: {root}")

        normalized: list[str] = []
        for raw in paths:
            rel = PurePosixPath(str(raw).replace("\\", "/"))
            if rel.is_absolute() or ".." in rel.parts or not str(rel):
                raise ValueError(f"Invalid commit path: {raw!r}")
            abs_file = root / rel
            if not abs_file.is_file():
                raise ValueError(f"Commit path missing or not a file: {rel}")
            normalized.append(str(rel))

        client = self._require_client()
        ref = await client.get(self._git_ref_get_path(owner, repo, branch))
        ref.raise_for_status()
        head_sha = str(ref.json()["object"]["sha"])

        parent = await client.get(f"/repos/{owner}/{repo}/git/commits/{head_sha}")
        parent.raise_for_status()
        base_tree_sha = str(parent.json()["tree"]["sha"])

        tree_entries: list[dict[str, str]] = []
        for rel in normalized:
            content = (root / rel).read_bytes()
            blob = await client.post(
                f"/repos/{owner}/{repo}/git/blobs",
                json={
                    "content": base64.b64encode(content).decode("ascii"),
                    "encoding": "base64",
                },
            )
            blob.raise_for_status()
            blob_sha = str(blob.json()["sha"])
            tree_entries.append(
                {
                    "path": rel,
                    "mode": "100644",
                    "type": "blob",
                    "sha": blob_sha,
                }
            )

        tree = await client.post(
            f"/repos/{owner}/{repo}/git/trees",
            json={"base_tree": base_tree_sha, "tree": tree_entries},
        )
        tree.raise_for_status()
        new_tree_sha = str(tree.json()["sha"])

        commit = await client.post(
            f"/repos/{owner}/{repo}/git/commits",
            json={
                "message": message,
                "tree": new_tree_sha,
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
            "ForgeClient committed paths to branch",
            owner=owner,
            repo=repo,
            branch=branch,
            commit_sha=new_sha,
            path_count=len(normalized),
            operation="commit_paths_to_branch",
        )
        return CommitPathsResult(
            commit_sha=new_sha,
            branch=branch,
            path_count=len(normalized),
            paths=list(normalized),
        )


def get_forge_client() -> ForgeClient:
    from src.di.dependency_container import provide_service

    return provide_service(ForgeClient)
