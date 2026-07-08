from __future__ import annotations

import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.risk import RiskAssessment, RiskScoreDto
from app.application.ports.repositories.risk_score_repository import RiskScoreRepository
from app.domain.value_objects.enums import Recommendation, RiskBand
from app.infrastructure.db.models.risk_score import RiskScore as RiskScoreModel


def _to_dto(model: RiskScoreModel) -> RiskScoreDto:
    return RiskScoreDto(
        id=model.id,
        application_id=model.application_id,
        score=float(model.score),
        band=model.band.value,
        recommendation=model.recommendation.value,
        confidence=float(model.confidence),
        component_scores=model.component_scores,
        weights_snapshot=model.weights_snapshot,
        reasons=model.reasons,
        created_at=model.created_at,
    )


class SqlAlchemyRiskScoreRepository(RiskScoreRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record(
        self,
        *,
        application_id: uuid.UUID,
        assessment: RiskAssessment,
        weights: dict[str, float],
        config_version: int,
    ) -> None:
        # Unset any prior current score first — the partial unique index
        # (one is_current row per application) would otherwise reject the insert.
        await self._session.execute(
            update(RiskScoreModel)
            .where(RiskScoreModel.application_id == application_id, RiskScoreModel.is_current)
            .values(is_current=False)
        )
        self._session.add(
            RiskScoreModel(
                application_id=application_id,
                score=assessment.score,
                band=RiskBand(assessment.band),
                recommendation=Recommendation(assessment.recommendation),
                confidence=assessment.confidence,
                component_scores=assessment.component_scores,
                weights_snapshot={**weights, "_config_version": config_version},
                reasons=assessment.reasons,
                is_current=True,
            )
        )
        await self._session.flush()

    async def get_current(self, application_id: uuid.UUID) -> RiskScoreDto | None:
        result = await self._session.execute(
            select(RiskScoreModel).where(
                RiskScoreModel.application_id == application_id, RiskScoreModel.is_current
            )
        )
        model = result.scalar_one_or_none()
        return _to_dto(model) if model else None

    async def get_current_batch(
        self, application_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, RiskScoreDto]:
        if not application_ids:
            return {}
        result = await self._session.execute(
            select(RiskScoreModel).where(
                RiskScoreModel.application_id.in_(application_ids), RiskScoreModel.is_current
            )
        )
        return {m.application_id: _to_dto(m) for m in result.scalars().all()}
