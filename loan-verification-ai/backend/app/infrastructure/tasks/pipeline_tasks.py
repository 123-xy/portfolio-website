from __future__ import annotations

import asyncio
import uuid

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.application.use_cases.verification.run_pipeline import RunVerificationPipeline
from app.core.config import get_settings
from app.infrastructure.ai.risk_scoring import AiServicesRiskScoringService
from app.infrastructure.ai.stage_runner import DeterministicStageRunner
from app.infrastructure.db.repositories.application_repository import (
    SqlAlchemyApplicationRepository,
)
from app.infrastructure.db.repositories.artifact_repository import SqlAlchemyArtifactRepository
from app.infrastructure.db.repositories.risk_engine_config_repository import (
    SqlAlchemyRiskEngineConfigRepository,
)
from app.infrastructure.db.repositories.risk_score_repository import SqlAlchemyRiskScoreRepository
from app.infrastructure.db.repositories.verification_result_repository import (
    SqlAlchemyVerificationResultRepository,
)
from app.infrastructure.storage.s3_storage import S3ObjectStorage
from app.infrastructure.tasks.celery_app import celery_app


async def _run(application_id: uuid.UUID) -> None:
    settings = get_settings()
    # A dedicated engine per task invocation avoids asyncpg connections being
    # bound to a stale event loop across successive asyncio.run() calls.
    engine = create_async_engine(str(settings.database_url), pool_pre_ping=True)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with sessionmaker() as session:
            use_case = RunVerificationPipeline(
                SqlAlchemyApplicationRepository(session),
                SqlAlchemyVerificationResultRepository(session),
                DeterministicStageRunner(
                    S3ObjectStorage(settings), SqlAlchemyArtifactRepository(session)
                ),
                SqlAlchemyRiskEngineConfigRepository(session),
                SqlAlchemyRiskScoreRepository(session),
                AiServicesRiskScoringService(),
            )
            await use_case.execute(application_id)
            await session.commit()
    finally:
        await engine.dispose()


@celery_app.task(name="verification.run_pipeline", bind=True, max_retries=3)
def run_verification_pipeline(self, application_id: str) -> None:  # type: ignore[no-untyped-def]
    """Celery entrypoint: run the async verification orchestrator for one
    application. Retries with backoff on transient (e.g. DB) errors."""
    try:
        asyncio.run(_run(uuid.UUID(application_id)))
    except Exception as exc:  # noqa: BLE001
        raise self.retry(exc=exc, countdown=5) from exc
