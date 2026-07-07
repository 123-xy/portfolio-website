from fastapi import APIRouter, Response, status

from app import __version__
from app.core.config import get_settings
from app.infrastructure.health.checks import check_database, check_redis
from app.interfaces.api.v1.schemas.health import (
    ComponentHealth,
    HealthResponse,
    ReadinessResponse,
)

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Liveness probe")
async def health() -> HealthResponse:
    """Liveness: the API process is running. Does not touch dependencies."""
    settings = get_settings()
    return HealthResponse(service=settings.app_name, version=__version__)


@router.get("/ready", response_model=ReadinessResponse, summary="Readiness probe")
async def ready(response: Response) -> ReadinessResponse:
    """Readiness: dependencies are reachable. Returns 503 if any is down so an
    orchestrator withholds traffic until the service can actually serve."""
    db_ok = await check_database()
    redis_ok = await check_redis()
    all_ok = db_ok and redis_ok
    if not all_ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return ReadinessResponse(
        status="ready" if all_ok else "degraded",
        components=ComponentHealth(database=db_ok, redis=redis_ok),
    )
