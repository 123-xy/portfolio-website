from __future__ import annotations

import uuid
from dataclasses import replace

from app.application.dto.reports import ReportDto
from app.application.ports.repositories.audit_log_repository import AuditLogRepository
from app.application.ports.repositories.report_repository import ReportRepository
from app.application.ports.services.object_storage import ObjectStorage
from app.domain.exceptions import NotFoundError
from app.domain.value_objects.enums import AuditAction


class GetReportDownloadUrl:
    """Re-issues a presigned URL for a previously generated report and logs a
    REPORT_EXPORTED audit entry — distinct from REPORT_GENERATED, so the
    trail shows both when a report was created and every time it was
    retrieved."""

    def __init__(
        self, reports: ReportRepository, storage: ObjectStorage, audit_log: AuditLogRepository
    ) -> None:
        self._reports = reports
        self._storage = storage
        self._audit_log = audit_log

    async def execute(self, report_id: uuid.UUID, requester_id: uuid.UUID) -> ReportDto:
        report = await self._reports.get_by_id(report_id)
        if report is None:
            raise NotFoundError("Report not found.")

        url = await self._storage.create_download_url(report.storage_key)
        await self._audit_log.log(
            action=AuditAction.REPORT_EXPORTED,
            actor_user_id=requester_id,
            application_id=report.application_id,
            target_type="report",
            target_id=report.id,
            metadata={"format": report.format.value},
        )
        return replace(report, download_url=url)
