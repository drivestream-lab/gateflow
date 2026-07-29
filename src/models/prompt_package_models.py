"""Pydantic models for pin prompt packages and bound-input rendering."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PromptVariableDecl(BaseModel):
    """One variable declaration from pin ``schema.yaml``."""

    model_config = ConfigDict(extra="forbid")

    required: bool = Field(default=False)
    type: str = Field(default="string")


class PromptPackageSchemaDocument(BaseModel):
    """Validated pin ``prompts/schema.yaml`` document."""

    model_config = ConfigDict(extra="forbid")

    prompt_id: str
    revision: str
    variables: dict[str, PromptVariableDecl] = Field(default_factory=dict)


class BoundPromptInputs(BaseModel):
    """Shared bind dictionary for packaged-skill automate (REQ-2 / ADR-010)."""

    model_config = ConfigDict(extra="forbid")

    ticket: str = Field(min_length=1)
    initiative: str = Field(default="")
    skill_id: str = Field(min_length=1)
    workspace: str = Field(min_length=1)
    handoff_path: str = Field(min_length=1)
    meta_workspace: Optional[str] = Field(default=None)
    meta_pr_url: Optional[str] = Field(default=None)


class ResolvedPromptPackage(BaseModel):
    """Resolved pin package ready for bind/render."""

    model_config = ConfigDict(extra="forbid")

    prompt_id: str
    prompt_revision: str
    template_text: str
    package_schema: PromptPackageSchemaDocument
    package_dir: str


class RenderedPrompt(BaseModel):
    """Render result — sole AgentRunner message body for packaged path."""

    model_config = ConfigDict(extra="forbid")

    message: str
    prompt_id: str
    prompt_revision: str


class PromptResolveError(ValueError):
    """Fail-closed package/bind/render error (stable reason for run/stage)."""

    def __init__(self, reason: str, *, detail: Optional[str] = None) -> None:
        self.reason = reason
        self.detail = detail
        message = reason if detail is None else f"{reason}: {detail}"
        super().__init__(message)
