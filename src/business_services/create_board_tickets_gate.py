"""Create-tickets triple predicate gate (REQ-06 / pin board-tickets-action requires)."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path, PurePosixPath

from src.exceptions.app_exceptions import UnprocessableEntityError
from src.models.work_manifest_models import run_workmanifest_contract

PREDICATE_SPEC_PR_MERGED = "spec-pr-merged"
PREDICATE_PLAN_CURRENT = "implementation-plan-current"
PREDICATE_WORKMANIFEST = "workmanifest-contract-pass"

_SPEC_BRANCH_RE = re.compile(r"^chore/.+-spec-.+$", re.IGNORECASE)


def canonical_implementation_plan_relpath(initiative: str) -> str:
    """Return the merged-plan path expected after spec PR merge."""
    cleaned = initiative.strip()
    if not cleaned:
        raise ValueError("initiative is required for plan path resolution")
    return f"docs/specification/reports/Implementation-Plan-{cleaned}.md"


class CreateBoardTicketsGateError(UnprocessableEntityError):
    """422 when any create-tickets predicate fails — 0 board creates."""

    def __init__(self, *, predicate: str, message: str) -> None:
        super().__init__(
            message=message,
            details={"predicate": predicate, "failed_predicates": [predicate]},
        )
        self.predicate = predicate


def evaluate_create_board_tickets_predicates(
    *,
    workspace: Path,
    plan_path: str,
    initiative: str,
    integration_branch: str = "develop",
) -> None:
    """Fail closed with 422 unless all three pin predicates pass."""
    root = workspace.resolve()
    if not root.is_dir():
        raise CreateBoardTicketsGateError(
            predicate=PREDICATE_SPEC_PR_MERGED,
            message=f"workspace_path is not a directory: {root}",
        )

    rel = PurePosixPath(str(plan_path).replace("\\", "/"))
    if rel.is_absolute() or ".." in rel.parts or not str(rel):
        raise CreateBoardTicketsGateError(
            predicate=PREDICATE_SPEC_PR_MERGED,
            message=f"Invalid plan_path: {plan_path!r}",
        )

    canonical = PurePosixPath(canonical_implementation_plan_relpath(initiative))
    if rel != canonical:
        raise CreateBoardTicketsGateError(
            predicate=PREDICATE_SPEC_PR_MERGED,
            message=(
                f"plan_path {plan_path!r} must match merged spec plan "
                f"{canonical_implementation_plan_relpath(initiative)!r}"
            ),
        )

    plan_file = (root / rel).resolve()
    try:
        plan_file.relative_to(root)
    except ValueError as exc:
        raise CreateBoardTicketsGateError(
            predicate=PREDICATE_SPEC_PR_MERGED,
            message="plan_path escapes workspace",
        ) from exc
    if not plan_file.is_file():
        raise CreateBoardTicketsGateError(
            predicate=PREDICATE_SPEC_PR_MERGED,
            message=f"Merged implementation plan not found: {rel}",
        )

    if _is_git_repo(root):
        branch = _current_branch(root)
        if branch and _SPEC_BRANCH_RE.match(branch):
            raise CreateBoardTicketsGateError(
                predicate=PREDICATE_SPEC_PR_MERGED,
                message=(
                    f"create_board_tickets requires integration branch context "
                    f"(current branch {branch!r} is an open spec lane)"
                ),
            )
        if not _path_on_branch(root, integration_branch, str(rel)):
            raise CreateBoardTicketsGateError(
                predicate=PREDICATE_SPEC_PR_MERGED,
                message=(
                    f"Merged implementation plan missing on integration branch "
                    f"{integration_branch!r}: {rel}"
                ),
            )
        if not _plan_matches_integration(root, integration_branch, str(rel), plan_file):
            raise CreateBoardTicketsGateError(
                predicate=PREDICATE_PLAN_CURRENT,
                message=(
                    f"Workspace plan differs from integration branch "
                    f"{integration_branch!r}: {rel}"
                ),
            )

    try:
        run_workmanifest_contract(workspace=root, plan_file=plan_file)
    except ValueError as exc:
        raise CreateBoardTicketsGateError(
            predicate=PREDICATE_WORKMANIFEST,
            message=str(exc),
        ) from exc


def _is_git_repo(root: Path) -> bool:
    proc = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"],
        check=False,
        capture_output=True,
        text=True,
    )
    return proc.returncode == 0 and (proc.stdout or "").strip() == "true"


def _current_branch(root: Path) -> str | None:
    proc = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--abbrev-ref", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return None
    branch = (proc.stdout or "").strip()
    return branch or None


def _path_on_branch(root: Path, branch: str, rel_path: str) -> bool:
    proc = subprocess.run(
        ["git", "-C", str(root), "cat-file", "-e", f"{branch}:{rel_path}"],
        check=False,
        capture_output=True,
        text=True,
    )
    return proc.returncode == 0


def _plan_matches_integration(
    root: Path,
    branch: str,
    rel_path: str,
    workspace_plan: Path,
) -> bool:
    proc = subprocess.run(
        ["git", "-C", str(root), "show", f"{branch}:{rel_path}"],
        check=False,
        capture_output=True,
    )
    if proc.returncode != 0:
        return False
    return proc.stdout == workspace_plan.read_bytes()
