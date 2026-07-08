from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.application.dto.officer_review import OfficerDecisionDto
from app.application.dto.reports import AnalyticsSummary, GenerateReportCommand, ReportDto
from app.application.dto.risk import RiskScoreDto
from app.application.ports.repositories.analytics_repository import AnalyticsRepository
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
from app.application.ports.services.object_storage import ObjectStat, ObjectStorage
from app.application.use_cases.reports.generate_application_report import (
    GenerateApplicationReport,
)
from app.application.use_cases.reports.generate_bulk_export import GenerateBulkExport
from app.application.use_cases.reports.get_analytics_summary import GetAnalyticsSummary
from app.application.use_cases.reports.get_report_download_url import GetReportDownloadUrl
from app.domain.entities.application import Application, CoApplicant
from app.domain.exceptions import NotFoundError, ValidationError
from app.domain.value_objects.enums import (
    ApplicationStatus,
    AuditAction,
    DecisionType,
    ReportFormat,
    UserRole,
)


class FakeApps(ApplicationRepository):
    def __init__(self, apps: list[Application]) -> None:
        self._apps = {a.id: a for a in apps}

    async def next_reference_no(self) -> str:  # pragma: no cover
        return "APP-2026-000001"

    async def create(self, **kw) -> Application:  # pragma: no cover
        raise NotImplementedError

    async def get_by_id(self, application_id: uuid.UUID) -> Application | None:
        return self._apps.get(application_id)

    async def list_for_applicant(self, applicant_id):  # pragma: no cover
        return []

    async def list_for_review(self):  # pragma: no cover
        return []

    async def list_all(self) -> list[Application]:
        return list(self._apps.values())

    async def set_status(self, *a, **kw) -> None:  # pragma: no cover
        pass


class FakeResults(VerificationResultRepository):
    async def next_attempt(self, application_id, stage):  # pragma: no cover
        return 1

    async def record(self, **kw) -> None:  # pragma: no cover
        pass

    async def latest_scalars(self, application_id):
        return {}


class FakeRiskScores(RiskScoreRepository):
    def __init__(self, current: RiskScoreDto | None = None) -> None:
        self._current = current

    async def record(self, **kw) -> None:  # pragma: no cover
        pass

    async def get_current(self, application_id):
        return self._current

    async def get_current_batch(self, application_ids):
        return {self._current.application_id: self._current} if self._current else {}


class FakeDecisions(OfficerDecisionRepository):
    def __init__(self, rows: list[OfficerDecisionDto] | None = None) -> None:
        self._rows = rows or []

    async def record(self, **kw) -> OfficerDecisionDto:  # pragma: no cover
        raise NotImplementedError

    async def list_for_application(self, application_id):
        return self._rows


class RecordingReports(ReportRepository):
    def __init__(self) -> None:
        self.created: list[dict[str, object]] = []
        self._store: dict[uuid.UUID, ReportDto] = {}

    async def next_version(self, application_id, format) -> int:
        return 1

    async def create(
        self, *, application_id, format, storage_key, generated_by, version
    ) -> ReportDto:
        report = ReportDto(
            id=uuid.uuid4(),
            application_id=application_id,
            format=format,
            storage_key=storage_key,
            version=version,
            created_at=datetime.now(UTC),
        )
        self.created.append(
            {"application_id": application_id, "format": format, "storage_key": storage_key}
        )
        self._store[report.id] = report
        return report

    async def get_by_id(self, report_id: uuid.UUID) -> ReportDto | None:
        return self._store.get(report_id)


class RecordingStorage(ObjectStorage):
    def __init__(self) -> None:
        self.uploaded: list[tuple[str, bytes, str]] = []

    async def ensure_bucket(self) -> None:  # pragma: no cover
        pass

    async def create_upload_url(  # pragma: no cover
        self, key, *, content_type, expires_seconds=900
    ) -> str:
        return ""

    async def create_download_url(self, key, *, expires_seconds=300) -> str:
        return f"https://storage.local/{key}"

    async def stat(self, key) -> ObjectStat | None:  # pragma: no cover
        return None

    async def download_bytes(self, key: str) -> bytes:  # pragma: no cover
        return b""

    async def upload_bytes(self, key: str, data: bytes, *, content_type: str) -> None:
        self.uploaded.append((key, data, content_type))

    async def delete(self, key: str) -> None:  # pragma: no cover
        pass


class RecordingAuditLog(AuditLogRepository):
    def __init__(self) -> None:
        self.entries: list[dict[str, object]] = []

    async def log(self, **kw) -> None:
        self.entries.append(kw)

    async def list_for_application(self, application_id):  # pragma: no cover
        return []


class FakeAnalytics(AnalyticsRepository):
    def __init__(self, summary: AnalyticsSummary) -> None:
        self._summary = summary

    async def get_summary(self) -> AnalyticsSummary:
        return self._summary


def _app(status: ApplicationStatus = ApplicationStatus.APPROVED) -> Application:
    return Application(
        id=uuid.uuid4(),
        reference_no="APP-2026-000042",
        applicant_id=uuid.uuid4(),
        loan_amount=Decimal("2200000"),
        status=status,
        loan_purpose="Home loan",
        co_applicant=CoApplicant(id=uuid.uuid4(), full_name="Spouse Name"),
    )


def _risk(application_id: uuid.UUID) -> RiskScoreDto:
    return RiskScoreDto(
        id=uuid.uuid4(),
        application_id=application_id,
        score=0.1,
        band="low",
        recommendation="auto_approve_candidate",
        confidence=0.9,
        component_scores={"face_match": 0.95},
        weights_snapshot={"face_match": 0.4},
        reasons=["Face match similarity 0.95"],
        created_at=datetime.now(UTC),
    )


# --- GenerateApplicationReport ---
@pytest.mark.parametrize("fmt", [ReportFormat.PDF, ReportFormat.JSON, ReportFormat.CSV])
async def test_generate_application_report_all_formats(fmt: ReportFormat) -> None:
    app = _app()
    storage, audit, reports = RecordingStorage(), RecordingAuditLog(), RecordingReports()
    decisions = FakeDecisions(
        [
            OfficerDecisionDto(
                id=uuid.uuid4(),
                decision=DecisionType.APPROVE,
                reason="ok",
                created_at=datetime.now(UTC),
            )
        ]
    )
    use_case = GenerateApplicationReport(
        FakeApps([app]),
        FakeResults(),
        FakeRiskScores(_risk(app.id)),
        decisions,
        reports,
        storage,
        audit,
    )

    result = await use_case.execute(
        GenerateReportCommand(app.id, fmt), uuid.uuid4(), UserRole.OFFICER, "officer@bank.com"
    )

    assert result.download_url is not None
    assert len(storage.uploaded) == 1
    assert len(reports.created) == 1
    assert audit.entries[0]["action"] == AuditAction.REPORT_GENERATED


async def test_generate_application_report_denies_applicant() -> None:
    app = _app()
    use_case = GenerateApplicationReport(
        FakeApps([app]), FakeResults(), FakeRiskScores(), FakeDecisions(), RecordingReports(),
        RecordingStorage(), RecordingAuditLog(),
    )
    with pytest.raises(NotFoundError):
        await use_case.execute(
            GenerateReportCommand(app.id, ReportFormat.PDF),
            app.applicant_id,
            UserRole.APPLICANT,
            "x",
        )


async def test_generate_application_report_404_unknown_application() -> None:
    use_case = GenerateApplicationReport(
        FakeApps([]), FakeResults(), FakeRiskScores(), FakeDecisions(), RecordingReports(),
        RecordingStorage(), RecordingAuditLog(),
    )
    with pytest.raises(NotFoundError):
        await use_case.execute(
            GenerateReportCommand(uuid.uuid4(), ReportFormat.PDF),
            uuid.uuid4(),
            UserRole.OFFICER,
            "x",
        )


# --- GenerateBulkExport ---
async def test_bulk_export_rejects_pdf() -> None:
    use_case = GenerateBulkExport(
        FakeApps([]), FakeRiskScores(), RecordingReports(), RecordingStorage(), RecordingAuditLog()
    )
    with pytest.raises(ValidationError):
        await use_case.execute(ReportFormat.PDF, uuid.uuid4())


async def test_bulk_export_covers_all_applications() -> None:
    apps = [_app(), _app(ApplicationStatus.REJECTED)]
    storage, reports = RecordingStorage(), RecordingReports()
    use_case = GenerateBulkExport(
        FakeApps(apps), FakeRiskScores(), reports, storage, RecordingAuditLog()
    )

    result = await use_case.execute(ReportFormat.CSV, uuid.uuid4())

    assert result.application_id is None  # bulk export
    body = storage.uploaded[0][1].decode("utf-8")
    assert body.count("\n") >= 2  # header + 2 rows (allow trailing newline)
    for app in apps:
        assert app.reference_no in body


# --- GetReportDownloadUrl ---
async def test_get_report_download_url_logs_export_and_returns_url() -> None:
    reports = RecordingReports()
    created = await reports.create(
        application_id=uuid.uuid4(), format=ReportFormat.PDF, storage_key="reports/x.pdf",
        generated_by=uuid.uuid4(), version=1,
    )
    audit = RecordingAuditLog()
    use_case = GetReportDownloadUrl(reports, RecordingStorage(), audit)

    result = await use_case.execute(created.id, uuid.uuid4())

    assert result.download_url == "https://storage.local/reports/x.pdf"
    assert audit.entries[0]["action"] == AuditAction.REPORT_EXPORTED


async def test_get_report_download_url_404_unknown_report() -> None:
    use_case = GetReportDownloadUrl(RecordingReports(), RecordingStorage(), RecordingAuditLog())
    with pytest.raises(NotFoundError):
        await use_case.execute(uuid.uuid4(), uuid.uuid4())


# --- GetAnalyticsSummary ---
async def test_analytics_summary_passthrough() -> None:
    summary = AnalyticsSummary(
        total_applications=10,
        status_counts={"approved": 6, "rejected": 2, "pending_review": 2},
        approved_count=6,
        rejected_count=2,
        approval_rate=0.75,
        risk_band_counts={"low": 7, "medium": 2, "high": 1},
        average_risk_score=0.22,
        average_confidence=0.91,
        average_decision_seconds=185.0,
    )
    result = await GetAnalyticsSummary(FakeAnalytics(summary)).execute()
    assert result.total_applications == 10
    assert result.approval_rate == 0.75
