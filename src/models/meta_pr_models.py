"""Meta PR accept-gate DTOs (ADR-010 / INIT-006 W4)."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class GithubPullRequestLabel(BaseModel):
    """Minimal GitHub label shape used for initiative derivation."""

    model_config = ConfigDict(extra="ignore")

    name: str = Field(default="")


class GithubPullRequestHead(BaseModel):
    """Minimal GitHub PR head shape."""

    model_config = ConfigDict(extra="ignore")

    sha: str = Field(default="")


class GithubPullRequestDocument(BaseModel):
    """Validated GitHub pull-request payload at the ForgeClient edge."""

    model_config = ConfigDict(extra="ignore")

    title: str = Field(default="")
    body: Optional[str] = Field(default=None)
    labels: list[GithubPullRequestLabel] = Field(default_factory=list)
    head: GithubPullRequestHead = Field(default_factory=GithubPullRequestHead)


class GithubIssueLabel(BaseModel):
    """Minimal GitHub issue label shape."""

    model_config = ConfigDict(extra="ignore")

    name: str = Field(default="")


class GithubIssueDocument(BaseModel):
    """Validated GitHub issue payload at the ForgeClient edge."""

    model_config = ConfigDict(extra="ignore")

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
