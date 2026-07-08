from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from app.application.ports.repositories.analytics_repository import AnalyticsRepository
from app.application.ports.repositories.report_repository import ReportRepository
from app.application.use_cases.reports.generate_application_report import (
    GenerateApplicationReport,
)
from app.application.use_cases.reports.generate_bulk_export import GenerateBulkExport
from app.application.use_cases.reports.get_analytics_summary import GetAnalyticsSummary
from app.application.use_cases.reports.get_report_download_url import GetReportDownloadUrl
from app.infrastructure.db.repositories.analytics_repository import SqlAlchemyAnalyticsRepository
from app.infrastructure.db.repositories.report_repository import SqlAlchemyReportRepository
from app.interfaces.api.v1.deps.applications import AppRepoDep, RiskScoreRepoDep, StorageDep
from app.interfaces.api.v1.deps.auth import SessionDep
from app.interfaces.api.v1.deps.officer import (
    AuditLogRepoDep,
    OfficerDecisionRepoDep,
    VerificationResultRepoDep,
)


def get_report_repository(session: SessionDep) -> ReportRepository:
    return SqlAlchemyReportRepository(session)


def get_analytics_repository(session: SessionDep) -> AnalyticsRepository:
    return SqlAlchemyAnalyticsRepository(session)


ReportRepoDep = Annotated[ReportRepository, Depends(get_report_repository)]
AnalyticsRepoDep = Annotated[AnalyticsRepository, Depends(get_analytics_repository)]


def get_generate_application_report(
    applications: AppRepoDep,
    results: VerificationResultRepoDep,
    risk_scores: RiskScoreRepoDep,
    decisions: OfficerDecisionRepoDep,
    reports: ReportRepoDep,
    storage: StorageDep,
    audit_log: AuditLogRepoDep,
) -> GenerateApplicationReport:
    return GenerateApplicationReport(
        applications, results, risk_scores, decisions, reports, storage, audit_log
    )


def get_generate_bulk_export(
    applications: AppRepoDep,
    risk_scores: RiskScoreRepoDep,
    reports: ReportRepoDep,
    storage: StorageDep,
    audit_log: AuditLogRepoDep,
) -> GenerateBulkExport:
    return GenerateBulkExport(applications, risk_scores, reports, storage, audit_log)


def get_get_report_download_url(
    reports: ReportRepoDep, storage: StorageDep, audit_log: AuditLogRepoDep
) -> GetReportDownloadUrl:
    return GetReportDownloadUrl(reports, storage, audit_log)


def get_get_analytics_summary(analytics: AnalyticsRepoDep) -> GetAnalyticsSummary:
    return GetAnalyticsSummary(analytics)


__all__ = [
    "get_generate_application_report",
    "get_generate_bulk_export",
    "get_get_report_download_url",
    "get_get_analytics_summary",
]
