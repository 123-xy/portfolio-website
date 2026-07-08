from __future__ import annotations

import uuid
from dataclasses import replace

from ai_services import render_bulk_csv, render_bulk_json
from ai_services.report_generator.contracts import BulkExportRow

from app.application.dto.reports import ReportDto
from app.application.ports.repositories.application_repository import ApplicationRepository
from app.application.ports.repositories.audit_log_repository import AuditLogRepository
from app.application.ports.repositories.report_repository import ReportRepository
from app.application.ports.repositories.risk_score_repository import RiskScoreRepository
from app.application.ports.services.object_storage import ObjectStorage
from app.domain.exceptions import ValidationError
from app.domain.value_objects.enums import AuditAction, ReportFormat

_CONTENT_TYPE = {ReportFormat.JSON: "application/json", ReportFormat.CSV: "text/csv"}
_EXTENSION = {ReportFormat.JSON: ".json", ReportFormat.CSV: ".csv"}


class GenerateBulkExport:
    """Compliance export of every application (reference, status, risk band,
    dates) as CSV or JSON. Callers are gated staff-only at the router; there
    is no single application to hide behind a 404 here."""

    def __init__(
        self,
        applications: ApplicationRepository,
        risk_scores: RiskScoreRepository,
        reports: ReportRepository,
        storage: ObjectStorage,
        audit_log: AuditLogRepository,
    ) -> None:
        self._applications = applications
        self._risk_scores = risk_scores
        self._reports = reports
        self._storage = storage
        self._audit_log = audit_log

    async def execute(
        self, format: ReportFormat, requester_id: uuid.UUID
    ) -> ReportDto:
        if format is ReportFormat.PDF:
            raise ValidationError("PDF is not supported for bulk export; use CSV or JSON.")

        apps = await self._applications.list_all()
        risk_by_app = await self._risk_scores.get_current_batch([a.id for a in apps])

        rows = [
            BulkExportRow(
                reference_no=a.reference_no,
                status=a.status.value,
                loan_amount=f"₹{float(a.loan_amount):,.0f}",
                co_applicant_name=a.co_applicant.full_name if a.co_applicant else None,
                risk_band=risk_by_app[a.id].band if a.id in risk_by_app else None,
                risk_score=risk_by_app[a.id].score if a.id in risk_by_app else None,
                submitted_at=a.submitted_at,
                decided_at=a.decided_at,
            )
            for a in apps
        ]
        content = render_bulk_csv(rows) if format is ReportFormat.CSV else render_bulk_json(rows)

        version = await self._reports.next_version(None, format)
        storage_key = f"reports/bulk/{format.value}/{uuid.uuid4()}{_EXTENSION[format]}"
        await self._storage.upload_bytes(storage_key, content, content_type=_CONTENT_TYPE[format])
        report = await self._reports.create(
            application_id=None,
            format=format,
            storage_key=storage_key,
            generated_by=requester_id,
            version=version,
        )

        download_url = await self._storage.create_download_url(storage_key)
        await self._audit_log.log(
            action=AuditAction.REPORT_GENERATED,
            actor_user_id=requester_id,
            application_id=None,
            target_type="report",
            target_id=report.id,
            metadata={"format": format.value, "row_count": len(rows)},
        )
        return replace(report, download_url=download_url)
