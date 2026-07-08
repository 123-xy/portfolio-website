from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.application.use_cases.reports.get_analytics_summary import GetAnalyticsSummary
from app.domain.value_objects.enums import UserRole
from app.interfaces.api.v1.deps.auth import require_role
from app.interfaces.api.v1.deps.reports import get_get_analytics_summary
from app.interfaces.api.v1.schemas.reports import AnalyticsSummaryResponse

router = APIRouter(prefix="/analytics", tags=["analytics"])

StaffOnly = Annotated[
    object, Depends(require_role(UserRole.OFFICER, UserRole.AUDITOR, UserRole.ADMIN))
]


@router.get(
    "",
    response_model=AnalyticsSummaryResponse,
    summary="Applications, approvals/rejections, risk trends, average confidence",
)
async def get_analytics_summary(
    _staff: StaffOnly,
    use_case: Annotated[GetAnalyticsSummary, Depends(get_get_analytics_summary)],
) -> AnalyticsSummaryResponse:
    summary = await use_case.execute()
    return AnalyticsSummaryResponse(
        total_applications=summary.total_applications,
        status_counts=summary.status_counts,
        approved_count=summary.approved_count,
        rejected_count=summary.rejected_count,
        approval_rate=summary.approval_rate,
        risk_band_counts=summary.risk_band_counts,
        average_risk_score=summary.average_risk_score,
        average_confidence=summary.average_confidence,
        average_decision_seconds=summary.average_decision_seconds,
    )
