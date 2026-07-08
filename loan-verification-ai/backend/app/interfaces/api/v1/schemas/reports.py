from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.domain.value_objects.enums import ReportFormat


class GenerateReportRequest(BaseModel):
    format: ReportFormat


class ReportResponse(BaseModel):
    id: uuid.UUID
    application_id: uuid.UUID | None
    format: ReportFormat
    version: int
    created_at: datetime
    download_url: str | None


class AnalyticsSummaryResponse(BaseModel):
    total_applications: int
    status_counts: dict[str, int]
    approved_count: int
    rejected_count: int
    approval_rate: float | None
    risk_band_counts: dict[str, int]
    average_risk_score: float | None
    average_confidence: float | None
    average_decision_seconds: float | None
