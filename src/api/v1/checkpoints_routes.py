"""Programme-token checkpoint status + history API (INIT-GATEFLOW-011 CAP-01/02)."""

from fastapi import APIRouter, Depends, Query

from src.api.v1.programme_token import verify_programme_service_token
from src.business_services.checkpoint_evidence_service import (
    CheckpointEvidenceService,
    get_checkpoint_evidence_service,
)
from src.exceptions.app_exceptions import ValidationError
from src.models.checkpoint_models import (
    CheckpointHistoryResult,
    CheckpointPrRef,
    CheckpointStatusResult,
)

router = APIRouter(prefix="/checkpoints")


def _resolve_pr_ref(
    service: CheckpointEvidenceService,
    owner: str | None,
    repo: str | None,
    pr_number: int | None,
    initiative_id: str | None,
    wave_id: str | None,
    checkpoint_id: str,
) -> CheckpointPrRef | None:
    """Resolve a PR reference from raw coords, or None when not supplied.

    Composed resolution (initiative+wave) is handled by the service on the
    composed path; this helper only resolves the raw-PR shape.
    """
    if owner is not None and repo is not None and pr_number is not None:
        return CheckpointPrRef(owner=owner, repo=repo, number=pr_number)
    return None


@router.get("/status", response_model=CheckpointStatusResult)
async def get_checkpoint_status(
    checkpoint_id: str = Query(..., description="Pin checkpoint node id"),
    owner: str | None = Query(default=None, description="GitHub org or user (raw ref)"),
    repo: str | None = Query(default=None, description="GitHub repository name (raw ref)"),
    pr_number: int | None = Query(default=None, ge=1, description="Pull request number (raw ref)"),
    initiative_id: str | None = Query(
        default=None, description="Initiative id (composed ref — resolves PR from run)"
    ),
    wave_id: str | None = Query(
        default=None, description="Wave id (composed ref — resolves PR from run)"
    ),
    _: None = Depends(verify_programme_service_token),
    service: CheckpointEvidenceService = Depends(get_checkpoint_evidence_service),
) -> CheckpointStatusResult:
    """Live CAP-01 status-check — read-only; never mutates GitHub or board.

    Caller supplies either raw PR coords (owner/repo/pr_number) or composed
    coords (initiative_id/wave_id). When initiative+wave is supplied and no run
    is found, returns 404 ``no run found for this wave``.
    """
    has_raw = owner is not None and repo is not None and pr_number is not None
    has_composed = initiative_id is not None and wave_id is not None
    if not has_raw and not has_composed:
        raise ValidationError(
            message="Supply either owner+repo+pr_number or initiative_id+wave_id",
        )
    if has_composed:
        assert initiative_id is not None and wave_id is not None
        return await service.evaluate_composed(
            initiative_id=initiative_id,
            wave_id=wave_id,
            checkpoint_id=checkpoint_id,
        )
    pr_ref = _resolve_pr_ref(service, owner, repo, pr_number, initiative_id, wave_id, checkpoint_id)
    assert pr_ref is not None
    return await service.evaluate(checkpoint_id, pr_ref)


@router.get("/history", response_model=CheckpointHistoryResult)
async def get_checkpoint_history(
    owner: str = Query(..., description="GitHub org or user"),
    repo: str = Query(..., description="GitHub repository name"),
    pr_number: int = Query(..., ge=1, description="Pull request number"),
    checkpoint_id: str | None = Query(default=None, description="Optional filter by checkpoint id"),
    limit: int = Query(default=50, ge=1, le=200, description="Max records to return"),
    skip: int = Query(default=0, ge=0, description="Records to skip"),
    _: None = Depends(verify_programme_service_token),
    service: CheckpointEvidenceService = Depends(get_checkpoint_evidence_service),
) -> CheckpointHistoryResult:
    """Historical ``checkpoint_check`` records — never a live verdict (REQ-07)."""
    return await service.list_history(
        CheckpointPrRef(owner=owner, repo=repo, number=pr_number),
        checkpoint_id=checkpoint_id,
        limit=limit,
        skip=skip,
    )
