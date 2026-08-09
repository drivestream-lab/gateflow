"""Programme catalogue DTOs (INIT-GATEFLOW-013 CAP-02 / REQ-05–07)."""

from pydantic import BaseModel, ConfigDict, Field


class CatalogueCandidate(BaseModel):
    """One selectable repo derived from the synced programme catalogue."""

    model_config = ConfigDict(extra="forbid")

    org: str = Field(min_length=1)
    repo: str = Field(min_length=1)
    service_key: str = Field(
        min_length=1,
        description="Key under service-catalog services map",
    )
    status: str = Field(min_length=1, description="Catalogue status string")


class ProgrammeCatalogueResponse(BaseModel):
    """GET …/programme/catalogue response."""

    model_config = ConfigDict(extra="forbid")

    programme_org: str
    candidates: list[CatalogueCandidate]
