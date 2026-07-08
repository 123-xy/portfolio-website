from __future__ import annotations

from abc import ABC, abstractmethod

from app.application.dto.reports import AnalyticsSummary


class AnalyticsRepository(ABC):
    @abstractmethod
    async def get_summary(self) -> AnalyticsSummary:
        """Aggregate metrics computed in the database (not by loading every
        row into Python) — status distribution, approval rate, risk-band
        distribution, average risk score/confidence, and average
        time-to-decision for applications that have been decided."""
        ...
