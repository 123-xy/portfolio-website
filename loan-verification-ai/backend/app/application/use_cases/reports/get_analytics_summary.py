from __future__ import annotations

from app.application.dto.reports import AnalyticsSummary
from app.application.ports.repositories.analytics_repository import AnalyticsRepository


class GetAnalyticsSummary:
    """Staff-only aggregate metrics for the analytics dashboard. RBAC is
    enforced at the router (no per-record ownership concept applies here, so
    there is nothing to hide behind a 404)."""

    def __init__(self, analytics: AnalyticsRepository) -> None:
        self._analytics = analytics

    async def execute(self) -> AnalyticsSummary:
        return await self._analytics.get_summary()
