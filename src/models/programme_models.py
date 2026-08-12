"""Programme entity DTOs (INIT-GATEFLOW-014 W1)."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.models.lane_types import LaneType
from src.models.programme_catalogue_models import CatalogueCandidate


class LaneRunnerDefault(BaseModel):
    """Default runner + model for one lane."""

    model_config = ConfigDict(extra="forbid")

    runner_id: str = Field(min_length=1, description="Catalogue runner id")
    model_id: Optional[str] = Field(default=None, description="Optional model id")


class ProgrammeLaneDefaultsDocument(BaseModel):
    """Per-lane runner/model defaults stored on the Programme (JSONB)."""

    model_config = ConfigDict(extra="forbid")

    defaults: dict[LaneType, LaneRunnerDefault] = Field(default_factory=dict)


class ProgrammeOnboardRequest(BaseModel):
    """POST body for platform_admin Programme validate-then-create.

    Workspace root comes from ``GATEFLOW_WORKSPACE_ROOT`` (not this body).
    """

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, description="Display name for the Programme")
    meta_org: str = Field(min_length=1, description="Meta repository org")
    meta_repo: str = Field(min_length=1, description="Meta repository name")
    meta_ref: Optional[str] = Field(default=None, description="Optional git ref")
    github_pat: str = Field(min_length=1, description="Programme-owned GitHub PAT")

    @model_validator(mode="before")
    @classmethod
    def _reject_agent_key_fields(cls, data: object) -> object:
        if isinstance(data, dict):
            for key in ("agent_key", "cursor_api_key", "agent_credential"):
                if key in data:
                    raise ValueError(f"{key} is not allowed on Programme onboard")
        return data


class ProgrammeReadModel(BaseModel):
    """Programme row for API/list (PAT never included)."""

    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    name: str
    tenant_id: UUID
    workspace_root: str
    meta_org: str
    meta_repo: str
    meta_ref: Optional[str] = None
    lane_defaults: ProgrammeLaneDefaultsDocument = Field(
        default_factory=ProgrammeLaneDefaultsDocument
    )
    github_app_id: Optional[str] = Field(
        default=None, description="Reserved unused App field (REQ-14)"
    )
    github_installation_id: Optional[str] = Field(
        default=None, description="Reserved unused App field (REQ-14)"
    )


class ProgrammeCreateResult(BaseModel):
    """Successful validate-then-create outcome."""

    model_config = ConfigDict(extra="forbid")

    programme_id: UUID
    tenant_id: UUID
    repo_catalogue: list[CatalogueCandidate]


class AttachTenantAdminRequest(BaseModel):
    """Attach or create a tenant_admin identity for a Programme."""

    model_config = ConfigDict(extra="forbid")

    credential_identifier: str = Field(min_length=1)
    password: str = Field(min_length=1)


class AttachTenantAdminResponse(BaseModel):
    """Attach outcome — identity id + minted JWT for the programme tenant."""

    model_config = ConfigDict(extra="forbid")

    user_id: UUID
    tenant_id: UUID
    programme_id: UUID
    access_token: str
    created: bool = Field(description="True when a new identity row was inserted")


class ProgrammeLaneDefaultsUpdateRequest(BaseModel):
    """Replace per-lane defaults on a Programme."""

    model_config = ConfigDict(extra="forbid")

    defaults: dict[LaneType, LaneRunnerDefault] = Field(default_factory=dict)


class ProgrammeWipeResult(BaseModel):
    """Outcome of a successful programme cutover wipe (REQ-35)."""

    model_config = ConfigDict(extra="forbid")

    programme_id: UUID
    tenant_id: UUID
    wiped: bool = Field(default=True, description="True when durable rows were cleared")
