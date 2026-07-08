from __future__ import annotations

import uuid
from dataclasses import replace
from decimal import Decimal

from ai_services import render_csv, render_json, render_pdf
from ai_services.report_generator.contracts import (
    ApplicationReportData,
    DecisionRecord,
    EvidenceSummary,
    RiskSummary,
)

from app.application.dto.reports import GenerateReportCommand, ReportDto
from app.application.ports.repositories.application_repository import ApplicationRepository
from app.application.ports.repositories.audit_log_repository import AuditLogRepository
from app.application.ports.repositories.officer_decision_repository import (
    OfficerDecisionRepository,
)
from app.application.ports.repositories.report_repository import ReportRepository
from app.application.ports.repositories.risk_score_repository import RiskScoreRepository
from app.application.ports.repositories.verification_result_repository import (
    VerificationResultRepository,
)
from app.application.ports.services.object_storage import ObjectStorage
from app.application.use_cases.applications.access import authorize_staff
from app.application.use_cases.officer_review.verification_mapping import (
    build_verification_details,
)
from app.domain.exceptions import NotFoundError
from app.domain.value_objects.enums import AuditAction, ReportFormat, UserRole

_CONTENT_TYPE = {
    ReportFormat.PDF: "application/pdf",
    ReportFormat.JSON: "application/json",
    ReportFormat.CSV: "text/csv",
}
_EXTENSION = {ReportFormat.PDF: ".pdf", ReportFormat.JSON: ".json", ReportFormat.CSV: ".csv"}


def _format_currency(amount: Decimal) -> str:
    return f"₹{float(amount):,.0f}"


class GenerateApplicationReport:
    """Renders and stores a per-application report (PDF/JSON/CSV) combining
    loan details, the current risk assessment, the evidence summary, and the
    full decision history. Staff-only — this is an official record of the
    verification, not applicant self-service."""

    def __init__(
        self,
        applications: ApplicationRepository,
        results: VerificationResultRepository,
        risk_scores: RiskScoreRepository,
        decisions: OfficerDecisionRepository,
        reports: ReportRepository,
        storage: ObjectStorage,
        audit_log: AuditLogRepository,
    ) -> None:
        self._applications = applications
        self._results = results
        self._risk_scores = risk_scores
        self._decisions = decisions
        self._reports = reports
        self._storage = storage
        self._audit_log = audit_log

    async def execute(
        self,
        command: GenerateReportCommand,
        requester_id: uuid.UUID,
        role: UserRole,
        generated_by_label: str,
    ) -> ReportDto:
        app = await self._applications.get_by_id(command.application_id)
        if app is None:
            raise NotFoundError("Application not found.")
        authorize_staff(role)

        risk = await self._risk_scores.get_current(app.id)
        scalars = await self._results.latest_scalars(app.id)
        details = build_verification_details(scalars)
        decision_rows = await self._decisions.list_for_application(app.id)

        data = ApplicationReportData(
            reference_no=app.reference_no,
            status=app.status.value,
            loan_amount=_format_currency(app.loan_amount),
            loan_purpose=app.loan_purpose,
            co_applicant_name=app.co_applicant.full_name if app.co_applicant else None,
            submitted_at=app.submitted_at,
            decided_at=app.decided_at,
            risk=(
                RiskSummary(
                    score=risk.score,
                    band=risk.band,
                    recommendation=risk.recommendation,
                    confidence=risk.confidence,
                    component_scores=risk.component_scores,
                    reasons=risk.reasons,
                )
                if risk
                else None
            ),
            evidence=EvidenceSummary(
                face_similarity=details.face_similarity,
                consent_status=details.consent_status,
                intent_aligned=details.intent_aligned,
                fraud_score=details.fraud_score,
            ),
            decisions=[
                DecisionRecord(decision=d.decision.value, reason=d.reason, created_at=d.created_at)
                for d in decision_rows
            ],
            generated_by=generated_by_label,
        )

        content = self._render(command.format, data)
        version = await self._reports.next_version(app.id, command.format)
        storage_key = (
            f"reports/{app.id}/{command.format.value}/{uuid.uuid4()}{_EXTENSION[command.format]}"
        )
        await self._storage.upload_bytes(
            storage_key, content, content_type=_CONTENT_TYPE[command.format]
        )
        report = await self._reports.create(
            application_id=app.id,
            format=command.format,
            storage_key=storage_key,
            generated_by=requester_id,
            version=version,
        )

        download_url = await self._storage.create_download_url(storage_key)
        await self._audit_log.log(
            action=AuditAction.REPORT_GENERATED,
            actor_user_id=requester_id,
            application_id=app.id,
            target_type="report",
            target_id=report.id,
            metadata={"format": command.format.value},
        )
        return replace(report, download_url=download_url)

    @staticmethod
    def _render(format: ReportFormat, data: ApplicationReportData) -> bytes:
        if format is ReportFormat.PDF:
            return render_pdf(data)
        if format is ReportFormat.JSON:
            return render_json(data)
        return render_csv(data)
