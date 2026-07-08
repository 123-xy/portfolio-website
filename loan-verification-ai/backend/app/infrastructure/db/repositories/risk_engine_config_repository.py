from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.risk import RiskEngineConfigDto
from app.application.ports.repositories.risk_engine_config_repository import (
    RiskEngineConfigRepository,
)
from app.domain.exceptions import NotFoundError
from app.infrastructure.db.models.risk_engine_config import RiskEngineConfig


class SqlAlchemyRiskEngineConfigRepository(RiskEngineConfigRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_active(self) -> RiskEngineConfigDto:
        result = await self._session.execute(
            select(RiskEngineConfig).where(RiskEngineConfig.is_active.is_(True))
        )
        model = result.scalar_one_or_none()
        if model is None:
            # Should never happen once the seed migration has run; surfaced as
            # a stage failure (needs_attention) rather than a silent default,
            # so a missing config is visibly an ops problem, not a data guess.
            raise NotFoundError("No active risk engine configuration.")
        return RiskEngineConfigDto(
            version=model.version, weights=model.weights, thresholds=model.thresholds
        )
