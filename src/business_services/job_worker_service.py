"""Worker job claim loop — stub handler for W0 (no AgentRunner)."""

from injector import inject

from src.business_services.base_business_service import BaseBusinessService
from src.database.postgres.repository.run_store_repository import JobRepository
from src.infra_services.postgres_service import PostgresService
from src.models.run_store_models import JobModel


class JobWorkerService(BaseBusinessService):
    """Claim pending jobs and mark them processed without AgentRunner (W0)."""

    @inject
    def __init__(
        self,
        postgres_service: PostgresService,
        job_repository: JobRepository,
    ) -> None:
        super().__init__()
        self._postgres_service = postgres_service
        self._job_repository = job_repository

    async def claim_and_process_one(self) -> JobModel | None:
        """Claim one job (SKIP LOCKED), stub-handle, mark processed. Returns job or None."""
        async with self._postgres_service.transaction() as session:
            job = await self._job_repository.claim_next(session)
            if job is None:
                return None
            if job.id is None:
                raise RuntimeError("Claimed job missing id")

            self.logger.info(
                "Stub-processing claimed job",
                job_id=str(job.id),
                delivery_id=job.delivery_id,
                event_type=job.payload.event_type,
            )
            # W0: no AgentRunner / PolicyEngine — acknowledge only.
            updated = await self._job_repository.mark_processed(session, job.id)
            return updated


def get_job_worker_service() -> JobWorkerService:
    from src.di.dependency_container import provide_service

    return provide_service(JobWorkerService)
