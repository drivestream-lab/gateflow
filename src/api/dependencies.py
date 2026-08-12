"""FastAPI dependencies for gateflow."""

from src.business_services.metrics_emitter import MetricsEmitter
from src.business_services.skill_efficacy_service import SkillEfficacyService
from src.infra_services.postgres_service import PostgresService
from src.infra_services.redis_service import RedisService


def get_postgres_service() -> PostgresService:
    from src.di.dependency_container import provide_service

    return provide_service(PostgresService)


def get_redis_service() -> RedisService:
    from src.di.dependency_container import provide_service

    return provide_service(RedisService)


def get_metrics_emitter() -> MetricsEmitter:
    from src.di.dependency_container import provide_service

    return provide_service(MetricsEmitter)


def get_skill_efficacy_service() -> SkillEfficacyService:
    from src.di.dependency_container import provide_service

    return provide_service(SkillEfficacyService)
