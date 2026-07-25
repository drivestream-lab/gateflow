"""JobWorkerService — claim jobs and delegate to RunOrchestrator."""

from injector import inject

from src.business_services.base_business_service import BaseBusinessService
from src.business_services.run_orchestrator import RunOrchestrator
from src.database.postgres.repository.run_store_repository import JobRepository
from src.infra_services.postgres_service import PostgresService
from src.models.run_store_models import JobModel


class JobWorkerService(BaseBusinessService):
    """Claim pending jobs, process via RunOrchestrator, mark processed or failed."""

    @inject
    def __init__(
        self,
        postgres_service: PostgresService,
        job_repository: JobRepository,
        run_orchestrator: RunOrchestrator,
    ) -> None:
        super().__init__()
        self._postgres_service = postgres_service
        self._job_repository = job_repository
        self._run_orchestrator = run_orchestrator

    async def claim_and_process_one(self) -> JobModel | None:
        """Claim one job, orchestrate, then mark processed or failed."""
        job: JobModel | None = None
        async with self._postgres_service.transaction() as session:
            job = await self._job_repository.claim_next(session)
            if job is None:
                return None

        if job.id is None:
            raise RuntimeError("Claimed job missing id")

        try:
            summary = await self._run_orchestrator.process_job(job)
            self.logger.info(
                "Job orchestration finished",
                job_id=str(job.id),
                run_id=str(summary.run_id) if summary.run_id else None,
                terminal_status=summary.terminal_status,
                dispatched=summary.dispatched,
            )
            async with self._postgres_service.transaction() as session:
                updated = await self._job_repository.mark_processed(session, job.id)
                return updated
        except Exception as exc:
            self.logger.exception(
                "Job orchestration failed",
                job_id=str(job.id),
                delivery_id=job.delivery_id,
            )
            async with self._postgres_service.transaction() as session:
                return await self._job_repository.mark_failed(session, job.id, str(exc))


def get_job_worker_service() -> JobWorkerService:
    from src.di.dependency_container import provide_service

    return provide_service(JobWorkerService)
