"""SkillEfficacyService — tenant-scoped skill/spec efficacy metrics (CAP-02)."""

from datetime import UTC, datetime, timedelta
from typing import Optional
from uuid import UUID

from injector import inject
from sqlalchemy.ext.asyncio import AsyncSession

from src.business_services.base_business_service import BaseBusinessService
from src.business_services.workflow_engine import WorkflowEngine
from src.configs.orchestration_settings import OrchestrationSettings
from src.database.postgres.repository.learning_repository import LearningRepository
from src.database.postgres.repository.run_store_repository import RunEventRepository
from src.models.run_store_types import RunOutcomeType
from src.models.skill_efficacy_models import (
    OUTCOME_VOCABULARY_NOT_YET_OBSERVED,
    SkillEfficacyNodeItem,
    SkillEfficacyResponse,
    StageCompletedEfficacyRow,
)


class SkillEfficacyService(BaseBusinessService):
    """Compose stage_completed + learning codify aggregates for CAP-02."""

    @inject
    def __init__(
        self,
        run_event_repository: RunEventRepository,
        learning_repository: LearningRepository,
        workflow_engine: WorkflowEngine,
    ) -> None:
        super().__init__()
        self._run_event_repository = run_event_repository
        self._learning_repository = learning_repository
        self._workflow_engine = workflow_engine
        self._settings = OrchestrationSettings.get_instance()

    async def get_skill_efficacy(
        self,
        session: AsyncSession,
        *,
        tenant_id: UUID,
        model_id: Optional[str] = None,
        prompt_revision: Optional[str] = None,
    ) -> SkillEfficacyResponse:
        cutoff = datetime.now(UTC) - timedelta(days=self._settings.metrics_retention_days)
        rows = await self._run_event_repository.list_stage_completed_for_tenant(
            session,
            tenant_id,
            since=cutoff,
        )
        boundary = await self._run_event_repository.min_extended_outcome_created_at(
            session,
            tenant_id,
        )
        boundary_label = (
            boundary.isoformat() if boundary is not None else OUTCOME_VOCABULARY_NOT_YET_OBSERVED
        )

        filtered = self._apply_filters(
            rows,
            model_id=model_id,
            prompt_revision=prompt_revision,
        )
        # Named-clean empty when filters match nothing (REQ-07).
        node_items = (
            []
            if (model_id is not None or prompt_revision is not None) and not filtered
            else self._aggregate_nodes(filtered)
        )

        known_nodes = self._workflow_engine.known_node_ids()
        codify = await self._learning_repository.aggregate_codify_rates(
            session,
            known_workflow_nodes=known_nodes,
        )
        codify_by_node = {item.workflow_node: item.codify_rate for item in codify.by_workflow_node}
        merged_nodes = [
            (
                item.model_copy(update={"codify_rate": codify_by_node[item.workflow_node]})
                if item.workflow_node in codify_by_node
                else item
            )
            for item in node_items
        ]

        self.logger.info(
            "Skill efficacy aggregated",
            tenant_id=str(tenant_id),
            node_count=len(merged_nodes),
            model_id=model_id,
            prompt_revision=prompt_revision,
        )
        return SkillEfficacyResponse(
            retention_days=self._settings.metrics_retention_days,
            tenant_id=tenant_id,
            model_id=model_id,
            prompt_revision=prompt_revision,
            outcome_vocabulary_available_since=boundary_label,
            by_workflow_node=merged_nodes,
            codify_org_wide=codify.org_wide,
            codify_unjoined=codify.unjoined,
        )

    @staticmethod
    def _apply_filters(
        rows: list[StageCompletedEfficacyRow],
        *,
        model_id: Optional[str],
        prompt_revision: Optional[str],
    ) -> list[StageCompletedEfficacyRow]:
        out = rows
        if model_id is not None:
            out = [r for r in out if r.model_id == model_id]
        if prompt_revision is not None:
            out = [r for r in out if r.prompt_revision == prompt_revision]
        return out

    def _aggregate_nodes(
        self,
        rows: list[StageCompletedEfficacyRow],
    ) -> list[SkillEfficacyNodeItem]:
        by_node: dict[str, list[StageCompletedEfficacyRow]] = {}
        for row in rows:
            by_node.setdefault(row.workflow_node, []).append(row)

        items: list[SkillEfficacyNodeItem] = []
        for node, node_rows in sorted(by_node.items()):
            # Outcome-aware rates exclude pre-fix Null outcomes (REQ-03).
            aware = [r for r in node_rows if r.outcome_type is not None]
            stage_count = len(aware)
            run_ids = {r.run_id for r in aware}
            run_count = len(run_ids)
            findings_count = sum(
                1 for r in aware if r.outcome_type == RunOutcomeType.FINDINGS.value
            )
            first_pass = self._count_first_pass_successes(aware)
            first_pass_rate = (float(first_pass) / float(stage_count)) if stage_count else 0.0
            findings_rate = (float(findings_count) / float(stage_count)) if stage_count else 0.0
            retry_avg = (float(stage_count) / float(run_count) - 1.0) if run_count else 0.0
            items.append(
                SkillEfficacyNodeItem(
                    workflow_node=node,
                    run_count=run_count,
                    stage_count=stage_count,
                    first_pass_rate=first_pass_rate,
                    findings_rate=findings_rate,
                    retry_avg=retry_avg,
                )
            )
        return items

    @staticmethod
    def _count_first_pass_successes(rows: list[StageCompletedEfficacyRow]) -> int:
        """Count success stages with no prior findings on the same node within the run."""
        ordered = sorted(rows, key=lambda r: (r.run_id.hex, r.created_at))
        seen_findings: set[UUID] = set()
        count = 0
        for row in ordered:
            if row.outcome_type == RunOutcomeType.FINDINGS.value:
                seen_findings.add(row.run_id)
                continue
            if row.outcome_type != RunOutcomeType.SUCCESS.value:
                continue
            if row.run_id in seen_findings:
                continue
            count += 1
        return count


def get_skill_efficacy_service() -> SkillEfficacyService:
    from src.di.dependency_container import provide_service

    return provide_service(SkillEfficacyService)
