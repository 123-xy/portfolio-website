from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.verification import StageOutcome
from app.application.ports.repositories.verification_result_repository import (
    VerificationResultRepository,
)
from app.domain.value_objects.enums import StageStatus, VerificationStage
from app.infrastructure.db.models.verification_result import VerificationResult as ResultModel


def _to_decimal(value: float | None) -> Decimal | None:
    return Decimal(str(round(value, 4))) if value is not None else None


class SqlAlchemyVerificationResultRepository(VerificationResultRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def next_attempt(self, application_id: uuid.UUID, stage: VerificationStage) -> int:
        result = await self._session.execute(
            select(func.coalesce(func.max(ResultModel.attempt), 0)).where(
                ResultModel.application_id == application_id,
                ResultModel.stage == stage,
            )
        )
        return int(result.scalar_one()) + 1

    async def record(
        self,
        *,
        application_id: uuid.UUID,
        stage: VerificationStage,
        attempt: int,
        outcome: StageOutcome,
    ) -> None:
        now = datetime.now(UTC)
        self._session.add(
            ResultModel(
                application_id=application_id,
                stage=stage,
                attempt=attempt,
                status=outcome.status,
                similarity_score=_to_decimal(outcome.similarity_score),
                confidence=_to_decimal(outcome.confidence),
                consent=outcome.consent,
                payload=outcome.payload or None,
                error_reason=outcome.error_reason,
                started_at=now,
                completed_at=now,
            )
        )
        await self._session.flush()

    async def latest_scalars(
        self, application_id: uuid.UUID
    ) -> dict[VerificationStage, dict[str, object]]:
        # Highest attempt per stage that completed.
        result = await self._session.execute(
            select(ResultModel)
            .where(
                ResultModel.application_id == application_id,
                ResultModel.status == StageStatus.COMPLETED,
            )
            .order_by(ResultModel.stage, ResultModel.attempt.desc())
        )
        latest: dict[VerificationStage, dict[str, object]] = {}
        for row in result.scalars().all():
            if row.stage in latest:
                continue  # first seen is the highest attempt due to ordering
            latest[row.stage] = {
                "similarity_score": float(row.similarity_score)
                if row.similarity_score is not None
                else None,
                "confidence": float(row.confidence) if row.confidence is not None else None,
                "consent": row.consent.value if row.consent is not None else None,
                "payload": row.payload,
            }
        return latest
