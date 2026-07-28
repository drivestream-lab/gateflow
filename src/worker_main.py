"""Worker process entry — claim Postgres jobs (ADR-001)."""

import asyncio
import os
import uuid

import dotenv

from src.configs.app_settings import AppSettings
from src.configs.github_settings import GithubSettings
from src.di.dependency_container import (
    close_all_services,
    configure_container,
    initialize_all_services,
    provide_service,
)
from src.business_services.job_worker_service import JobWorkerService
from src.logging import LoggingContext, get_logger, setup_logging

POLL_INTERVAL_SECONDS = 2.0


async def run_worker_loop() -> None:
    logger = get_logger()
    worker = provide_service(JobWorkerService)
    logger.info("Worker claim loop started", poll_interval_seconds=POLL_INTERVAL_SECONDS)
    while True:
        try:
            job = await worker.claim_and_process_one()
            if job is None:
                await asyncio.sleep(POLL_INTERVAL_SECONDS)
        except asyncio.CancelledError:
            logger.info("Worker loop cancelled")
            raise
        except Exception:
            logger.exception("Worker iteration failed")
            await asyncio.sleep(POLL_INTERVAL_SECONDS)


async def async_main() -> None:
    startup_correlation_id = str(uuid.uuid4())
    with LoggingContext(startup_correlation_id):
        GithubSettings.get_instance()
        configure_container()
        await initialize_all_services()
        logger = get_logger()
        logger.info("Worker services initialized")
        try:
            await run_worker_loop()
        finally:
            await close_all_services()


def main() -> None:
    dotenv_path = os.path.join(os.getcwd(), ".env")
    if os.path.exists(dotenv_path):
        dotenv.load_dotenv(dotenv_path=dotenv_path, override=True)
    settings = AppSettings.get_instance()
    setup_logging(settings)
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
