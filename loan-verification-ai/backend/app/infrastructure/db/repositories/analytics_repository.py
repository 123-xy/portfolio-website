from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.reports import AnalyticsSummary
from app.application.ports.repositories.analytics_repository import AnalyticsRepository
from app.domain.value_objects.enums import ApplicationStatus
from app.infrastructure.db.models.application import Application as AppModel
from app.infrastructure.db.models.risk_score import RiskScore as RiskScoreModel


class SqlAlchemyAnalyticsRepository(AnalyticsRepository):
    """All aggregation happens in the database (GROUP BY / AVG), not by
    loading every application into Python — this stays cheap as the table
    grows."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_summary(self) -> AnalyticsSummary:
        status_rows = await self._session.execute(
            select(AppModel.status, func.count()).group_by(AppModel.status)
        )
        status_counts = {status.value: count for status, count in status_rows.all()}
        total = sum(status_counts.values())
        approved = status_counts.get(ApplicationStatus.APPROVED.value, 0)
        rejected = status_counts.get(ApplicationStatus.REJECTED.value, 0)
        decided_total = approved + rejected
        approval_rate = (approved / decided_total) if decided_total > 0 else None

        risk_rows = await self._session.execute(
            select(RiskScoreModel.band, func.count())
            .where(RiskScoreModel.is_current)
            .group_by(RiskScoreModel.band)
        )
        risk_band_counts = {band.value: count for band, count in risk_rows.all()}

        risk_avgs = await self._session.execute(
            select(func.avg(RiskScoreModel.score), func.avg(RiskScoreModel.confidence)).where(
                RiskScoreModel.is_current
            )
        )
        avg_score, avg_confidence = risk_avgs.one()

        decision_seconds = await self._session.execute(
            select(
                func.avg(
                    func.extract("epoch", AppModel.decided_at - AppModel.submitted_at)
                )
            ).where(AppModel.decided_at.is_not(None), AppModel.submitted_at.is_not(None))
        )
        avg_decision_seconds = decision_seconds.scalar_one()

        return AnalyticsSummary(
            total_applications=total,
            status_counts=status_counts,
            approved_count=approved,
            rejected_count=rejected,
            approval_rate=round(approval_rate, 4) if approval_rate is not None else None,
            risk_band_counts=risk_band_counts,
            average_risk_score=float(avg_score) if avg_score is not None else None,
            average_confidence=float(avg_confidence) if avg_confidence is not None else None,
            average_decision_seconds=(
                float(avg_decision_seconds) if avg_decision_seconds is not None else None
            ),
        )
