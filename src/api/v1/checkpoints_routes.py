"""Programme-token checkpoint status API (INIT-GATEFLOW-011 CAP-01)."""

from fastapi import APIRouter, Depends, Query

from src.api.v1.programme_token import verify_programme_service_token
from src.business_services.checkpoint_evidence_service import (
    CheckpointEvidenceService,
    get_checkpoint_evidence_service,
)
from src.models.checkpoint_models import CheckpointPrRef, CheckpointStatusResult

router = APIRouter(prefix="/checkpoints")


@router.get("/status", response_model=CheckpointStatusResult)
async def get_checkpoint_status(
    checkpoint_id: str = Query(..., description="Pin checkpoint node id"),
    owner: str = Query(..., description="GitHub org or user"),
    repo: str = Query(..., description="GitHub repository name"),
    pr_number: int = Query(..., ge=1, description="Pull request number"),
    _: None = Depends(verify_programme_service_token),
    service: CheckpointEvidenceService = Depends(get_checkpoint_evidence_service),
) -> CheckpointStatusResult:
    """Live CAP-01 status-check — read-only; never mutates GitHub or board."""
    return await service.evaluate(
        checkpoint_id,
        CheckpointPrRef(owner=owner, repo=repo, number=pr_number),
    )
