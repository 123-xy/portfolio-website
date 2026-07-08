from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from app.domain.value_objects.enums import ReportFormat


@dataclass(frozen=True)
class GenerateReportCommand:
    application_id: uuid.UUID
    format: ReportFormat


@dataclass(frozen=True)
class ReportDto:
    id: uuid.UUID
    application_id: uuid.UUID | None
    format: ReportFormat
    storage_key: str
    version: int
    created_at: datetime
    download_url: str | None = None


@dataclass(frozen=True)
class AnalyticsSummary:
    total_applications: int
    status_counts: dict[str, int]
    approved_count: int
    rejected_count: int
    approval_rate: float | None
    risk_band_counts: dict[str, int]
    average_risk_score: float | None
    average_confidence: float | None
    average_decision_seconds: float | None
