"""Main entry point for Gateflow."""

import os
import uuid
from pathlib import Path

import dotenv
import uvicorn

from src.app import create_app
from src.configs.app_settings import AppSettings
from src.logging import LoggingContext, get_logger, setup_logging

startup_correlation_id = str(uuid.uuid4())
dotenv_path = os.path.join(os.getcwd(), ".env")
if os.path.exists(dotenv_path):
    dotenv.load_dotenv(dotenv_path=dotenv_path, override=True)

settings = AppSettings.get_instance()
setup_logging(settings)
logger = get_logger()


def get_application():
    with LoggingContext(startup_correlation_id):
        return create_app()


def _dev_reload_excludes(root: Path) -> list[str]:
    """Absolute dir excludes — FileFilter matches against Path.parents."""
    exclude_dirs = [
        root / ".venv",
        root / "tests",
        root / "logs",
        root / "docs",
        root / "prayog-skills",
        root / ".gateflow",
        root / ".git",
        root / "postgres_migrations",
        root / "__pycache__",
    ]
    return [str(path) for path in exclude_dirs if path.exists()]


if __name__ == "__main__":
    root = Path.cwd()
    logger.info("Starting gateflow application", host=settings.host, port=settings.port)
    if settings.is_development:
        uvicorn.run(
            "src.main:get_application",
            host=settings.host,
            port=settings.port,
            reload=True,
            reload_dirs=[str(root / "src"), str(root)],
            reload_includes=["*.py", ".env"],
            reload_excludes=_dev_reload_excludes(root),
            log_level=settings.log_level.lower(),
            factory=True,
        )
    else:
        uvicorn.run(
            "src.main:get_application",
            host=settings.host,
            port=settings.port,
            reload=False,
            log_level=settings.log_level.lower(),
            factory=True,
        )
