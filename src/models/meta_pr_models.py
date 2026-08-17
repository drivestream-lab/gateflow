"""Meta PR accept-gate DTOs (ADR-010 / INIT-006 W4) + CAP-01 read shapes (INIT-011)."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class GithubPullRequestLabel(BaseModel):
    """Minimal GitHub label shape used for initiative derivation."""

    model_config = ConfigDict(extra="ignore")

    name: str = Field(default="")


class GithubPullRequestRef(BaseModel):
    """Minimal GitHub PR head/base ref shape (branch tip)."""

    model_config = ConfigDict(extra="ignore")

    ref: str = Field(default="", description="Branch name, e.g. feature/INIT-…-w0-…")
    sha: str = Field(default="")


class GithubPullRequestHead(GithubPullRequestRef):
    """Minimal GitHub PR head shape (compat alias)."""


class GithubPullRequestBase(GithubPullRequestRef):
    """Minimal GitHub PR base shape."""


class GithubPullRequestUser(BaseModel):
    """Minimal GitHub user shape on review payloads."""

    model_config = ConfigDict(extra="ignore")

    login: str = Field(default="")


class GithubPullRequestReviewDocument(BaseModel):
    """Validated GitHub pull-request review at the ForgeClient edge (CAP-01)."""

    model_config = ConfigDict(extra="ignore")

    id: Optional[int] = Field(default=None)
    user: GithubPullRequestUser = Field(default_factory=GithubPullRequestUser)
    state: str = Field(default="", description="APPROVED | CHANGES_REQUESTED | COMMENTED | …")
    submitted_at: Optional[datetime] = Field(default=None)
    commit_id: Optional[str] = Field(default=None)


class GithubCheckRunDocument(BaseModel):
    """Validated GitHub check-run at the ForgeClient edge (CAP-01)."""

    model_config = ConfigDict(extra="ignore")

    name: str = Field(default="")
    status: str = Field(default="", description="queued | in_progress | completed | …")
    conclusion: Optional[str] = Field(
        default=None, description="success | failure | neutral | … when completed"
    )
    head_sha: str = Field(default="")


class GithubPullRequestDocument(BaseModel):
    """Validated GitHub pull-request payload at the ForgeClient edge."""

    model_config = ConfigDict(extra="ignore")

    number: Optional[int] = Field(default=None, description="GitHub pull-request number")
    html_url: Optional[str] = Field(default=None, description="Canonical GitHub HTML URL")
    title: str = Field(default="")
    body: Optional[str] = Field(default=None)
    state: str = Field(default="", description="open | closed")
    labels: list[GithubPullRequestLabel] = Field(default_factory=list)
    head: GithubPullRequestHead = Field(default_factory=GithubPullRequestHead)
    base: GithubPullRequestBase = Field(default_factory=GithubPullRequestBase)
    merged: bool = Field(default=False, description="Whether the PR is merged")
    merge_commit_sha: Optional[str] = Field(default=None)
    merged_at: Optional[datetime] = Field(default=None)


class GithubIssueLabel(BaseModel):
    """Minimal GitHub issue label shape."""

    model_config = ConfigDict(extra="ignore")

    name: str = Field(default="")


class GithubIssueDocument(BaseModel):
    """Validated GitHub issue payload at the ForgeClient edge."""

    model_config = ConfigDict(extra="ignore")

    id: Optional[int] = Field(
        default=None,
        description="GitHub database id (required for sub-issue linking)",
    )
    number: int
    title: str = Field(default="")
    state: str = Field(default="open")
    body: Optional[str] = Field(default=None)
    html_url: Optional[str] = Field(default=None)
    labels: list[GithubIssueLabel] = Field(default_factory=list)


class MetaPrRef(BaseModel):
    """Parsed meta PR coordinates from a URL."""

    model_config = ConfigDict(extra="forbid")

    owner: str
    repo: str
    pr_number: int
    source_url: str


class MetaPrAcceptResult(BaseModel):
    """Accept-gate outcome persisted on the run for audit."""

    model_config = ConfigDict(extra="forbid")

    meta_pr_url: str
    meta_owner: str
    meta_repo: str
    meta_pr_number: int
    meta_head_sha: str
    derived_initiative_id: Optional[str] = Field(default=None)
