from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from app.application.dto.reports import GenerateReportCommand, ReportDto
from app.application.use_cases.reports.generate_application_report import (
    GenerateApplicationReport,
)
from app.application.use_cases.reports.generate_bulk_export import GenerateBulkExport
from app.application.use_cases.reports.get_report_download_url import GetReportDownloadUrl
from app.domain.value_objects.enums import UserRole
from app.interfaces.api.v1.deps.auth import CurrentUser, require_role
from app.interfaces.api.v1.deps.reports import (
    get_generate_application_report,
    get_generate_bulk_export,
    get_get_report_download_url,
)
from app.interfaces.api.v1.schemas.reports import GenerateReportRequest, ReportResponse

# No shared prefix: report generation is nested under /applications/{id},
# bulk export and download are top-level /reports resources.
router = APIRouter(tags=["reports"])

StaffOnly = Annotated[
    object, Depends(require_role(UserRole.OFFICER, UserRole.AUDITOR, UserRole.ADMIN))
]


def _response(report: ReportDto) -> ReportResponse:
    return ReportResponse(
        id=report.id,
        application_id=report.application_id,
        format=report.format,
        version=report.version,
        created_at=report.created_at,
        download_url=report.download_url,
    )


@router.post(
    "/applications/{application_id}/reports",
    response_model=ReportResponse,
    summary="Generate a per-application report (PDF/JSON/CSV)",
)
async def generate_application_report(
    application_id: uuid.UUID,
    body: GenerateReportRequest,
    current_user: CurrentUser,
    _staff: StaffOnly,
    use_case: Annotated[GenerateApplicationReport, Depends(get_generate_application_report)],
) -> ReportResponse:
    report = await use_case.execute(
        GenerateReportCommand(application_id=application_id, format=body.format),
        current_user.id,
        current_user.role,
        current_user.full_name,
    )
    return _response(report)


@router.post(
    "/reports/bulk",
    response_model=ReportResponse,
    summary="Generate a compliance bulk export (CSV/JSON) of every application",
)
async def generate_bulk_export(
    body: GenerateReportRequest,
    current_user: CurrentUser,
    _staff: StaffOnly,
    use_case: Annotated[GenerateBulkExport, Depends(get_generate_bulk_export)],
) -> ReportResponse:
    report = await use_case.execute(body.format, current_user.id)
    return _response(report)


@router.get(
    "/reports/{report_id}/download",
    response_model=ReportResponse,
    summary="Re-issue a presigned download URL for a previously generated report",
)
async def get_report_download_url(
    report_id: uuid.UUID,
    current_user: CurrentUser,
    _staff: StaffOnly,
    use_case: Annotated[GetReportDownloadUrl, Depends(get_get_report_download_url)],
) -> ReportResponse:
    report = await use_case.execute(report_id, current_user.id)
    return _response(report)
