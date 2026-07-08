from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.application.dto.officer_review import (
    AuditEntryDto,
    OfficerDecisionDto,
    RecordDecisionCommand,
)
from app.application.dto.risk import RiskScoreDto
from app.application.ports.repositories.application_repository import ApplicationRepository
from app.application.ports.repositories.audit_log_repository import AuditLogRepository
from app.application.ports.repositories.officer_decision_repository import (
    OfficerDecisionRepository,
)
from app.application.ports.repositories.officer_repository import OfficerDto, OfficerRepository
from app.application.ports.repositories.risk_score_repository import RiskScoreRepository
from app.application.ports.repositories.verification_result_repository import (
    VerificationResultRepository,
)
from app.application.use_cases.officer_review.get_artifact_download_url import (
    GetArtifactDownloadUrl,
)
from app.application.use_cases.officer_review.get_audit_trail import GetAuditTrail
from app.application.use_cases.officer_review.get_verification_details import (
    GetVerificationDetails,
)
from app.application.use_cases.officer_review.record_officer_decision import (
    RecordOfficerDecision,
)
from app.domain.entities.application import Application, Artifact
from app.domain.exceptions import InvalidStateTransitionError, NotFoundError, ValidationError
from app.domain.value_objects.enums import (
    ApplicationStatus,
    AuditAction,
    DecisionType,
    UserRole,
    VerificationStage,
)
from tests.unit.test_upload_use_cases import FakeStorage


class FakeApps(ApplicationRepository):
    def __init__(self, app: Application) -> None:
        self._app = app
        self.status_changes: list[tuple[ApplicationStatus, bool, bool]] = []

    async def next_reference_no(self) -> str:  # pragma: no cover
        return "APP-2026-000001"

    async def create(self, **kw) -> Application:  # pragma: no cover
        return self._app

    async def get_by_id(self, application_id: uuid.UUID) -> Application | None:
        return self._app if application_id == self._app.id else None

    async def list_for_applicant(self, applicant_id):  # pragma: no cover
        return []

    async def list_for_review(self):  # pragma: no cover
        return []

    async def list_all(self):  # pragma: no cover
        return []

    async def set_status(
        self, application_id, status, *, mark_submitted=False, mark_decided=False
    ) -> None:
        self._app.status = status
        self.status_changes.append((status, mark_submitted, mark_decided))


class FakeResults(VerificationResultRepository):
    def __init__(self, scalars: dict[VerificationStage, dict[str, object]]) -> None:
        self._scalars = scalars

    async def next_attempt(self, application_id, stage):  # pragma: no cover
        return 1

    async def record(self, **kw) -> None:  # pragma: no cover
        pass

    async def latest_scalars(self, application_id):
        return self._scalars


class FakeOfficers(OfficerRepository):
    def __init__(self, mapping: dict[uuid.UUID, OfficerDto]) -> None:
        self._mapping = mapping

    async def get_by_user_id(self, user_id: uuid.UUID) -> OfficerDto | None:
        return self._mapping.get(user_id)


class RecordingDecisions(OfficerDecisionRepository):
    def __init__(self) -> None:
        self.recorded: list[dict[str, object]] = []

    async def record(self, **kw) -> OfficerDecisionDto:
        self.recorded.append(kw)
        return OfficerDecisionDto(
            id=uuid.uuid4(),
            decision=kw["decision"],
            reason=kw["reason"],
            created_at=datetime.now(UTC),
        )

    async def list_for_application(self, application_id):  # pragma: no cover
        return []


class FakeRiskScores(RiskScoreRepository):
    def __init__(self, current: RiskScoreDto | None = None) -> None:
        self._current = current

    async def record(self, **kw) -> None:  # pragma: no cover
        pass

    async def get_current(self, application_id):
        return self._current

    async def get_current_batch(self, application_ids):  # pragma: no cover
        return {}


class RecordingAuditLog(AuditLogRepository):
    def __init__(self) -> None:
        self.entries: list[AuditEntryDto] = []
        self._application_ids: list[uuid.UUID | None] = []

    async def log(
        self,
        *,
        action: AuditAction,
        actor_user_id: uuid.UUID | None,
        application_id: uuid.UUID | None,
        target_type: str | None = None,
        target_id: uuid.UUID | None = None,
        metadata: dict[str, object] | None = None,
    ) -> None:
        self.entries.append(
            AuditEntryDto(
                id=uuid.uuid4(),
                action=action.value,
                actor_user_id=actor_user_id,
                is_system=actor_user_id is None,
                target_type=target_type,
                target_id=target_id,
                metadata=metadata,
                created_at=datetime.now(UTC),
            )
        )
        self._application_ids.append(application_id)

    async def list_for_application(self, application_id: uuid.UUID) -> list[AuditEntryDto]:
        return [
            e
            for e, app_id in zip(self.entries, self._application_ids, strict=True)
            if app_id == application_id
        ]


def _app(status: ApplicationStatus = ApplicationStatus.PENDING_REVIEW) -> Application:
    return Application(
        id=uuid.uuid4(),
        reference_no="APP-2026-000001",
        applicant_id=uuid.uuid4(),
        loan_amount=Decimal("100000"),
        status=status,
        artifacts=[
            Artifact(
                id=uuid.uuid4(),
                application_id=uuid.uuid4(),
                kind="applicant_photo",
                status="uploaded",
                storage_key="k/photo",
            )
        ],
    )


# --- GetVerificationDetails ---
async def test_verification_details_flattens_stage_payloads() -> None:
    app = _app()
    scalars: dict[VerificationStage, dict[str, object]] = {
        VerificationStage.FACE_MATCH: {"similarity_score": 0.9, "confidence": 0.95},
        VerificationStage.TRANSCRIPTION: {
            "confidence": 0.9,
            "payload": {"language": "en", "transcript": "I agree and consent."},
        },
        VerificationStage.CONSENT_DETECTION: {
            "consent": "explicit_yes",
            "confidence": 0.98,
            "payload": {"matched_phrases": ["i agree"]},
        },
        VerificationStage.INTENT_ANALYSIS: {
            "confidence": 0.9,
            "payload": {"aligned": True, "label": "coapplicant_intent_confirmed", "reasons": ["x"]},
        },
        VerificationStage.FRAUD_CHECK: {
            "confidence": 0.8,
            "payload": {"fraud_score": 0.1, "signals": []},
        },
    }
    details = await GetVerificationDetails(FakeApps(app), FakeResults(scalars)).execute(
        app.id, uuid.uuid4(), UserRole.OFFICER
    )
    assert details.face_similarity == 0.9
    assert details.transcript_text == "I agree and consent."
    assert details.consent_status == "explicit_yes"
    assert details.consent_matched_phrases == ["i agree"]
    assert details.intent_aligned is True
    assert details.fraud_score == 0.1


async def test_verification_details_denies_applicant() -> None:
    app = _app()
    with pytest.raises(NotFoundError):
        await GetVerificationDetails(FakeApps(app), FakeResults({})).execute(
            app.id, app.applicant_id, UserRole.APPLICANT
        )


# --- GetArtifactDownloadUrl ---
async def test_artifact_download_url_logs_audit_entry() -> None:
    app = _app()
    artifact_id = app.artifacts[0].id
    storage = FakeStorage()
    audit = RecordingAuditLog()
    officer_id = uuid.uuid4()

    url = await GetArtifactDownloadUrl(FakeApps(app), storage, audit).execute(
        app.id, artifact_id, officer_id, UserRole.OFFICER
    )
    assert url.startswith("https://storage.local/")
    assert len(audit.entries) == 1
    assert audit.entries[0].action == AuditAction.ARTIFACT_VIEWED.value
    assert audit.entries[0].actor_user_id == officer_id


async def test_artifact_download_url_404_for_unknown_artifact() -> None:
    app = _app()
    with pytest.raises(NotFoundError):
        await GetArtifactDownloadUrl(FakeApps(app), FakeStorage(), RecordingAuditLog()).execute(
            app.id, uuid.uuid4(), uuid.uuid4(), UserRole.OFFICER
        )


# --- RecordOfficerDecision ---
async def test_record_decision_approve_transitions_and_audits() -> None:
    app = _app()
    officer_user_id = uuid.uuid4()
    officer_dto = OfficerDto(id=uuid.uuid4(), user_id=officer_user_id, employee_code="EMP-1")
    apps, decisions, audit = FakeApps(app), RecordingDecisions(), RecordingAuditLog()
    current_risk = RiskScoreDto(
        id=uuid.uuid4(),
        application_id=app.id,
        score=0.1,
        band="low",
        recommendation="auto_approve_candidate",
        confidence=0.9,
        component_scores={},
        weights_snapshot={},
        reasons=[],
        created_at=datetime.now(UTC),
    )
    risk_scores = FakeRiskScores(current_risk)
    use_case = RecordOfficerDecision(
        apps, FakeOfficers({officer_user_id: officer_dto}), decisions, risk_scores, audit
    )

    result = await use_case.execute(
        RecordDecisionCommand(app.id, DecisionType.APPROVE, "Looks good, evidence checks out."),
        officer_user_id,
    )

    assert result.decision is DecisionType.APPROVE
    assert app.status is ApplicationStatus.APPROVED
    assert apps.status_changes[-1] == (ApplicationStatus.APPROVED, False, True)
    assert decisions.recorded[0]["risk_score_id"] == current_risk.id
    assert len(audit.entries) == 1
    assert audit.entries[0].action == AuditAction.OFFICER_DECISION.value


async def test_record_decision_request_more_info_is_not_terminal() -> None:
    app = _app()
    officer_user_id = uuid.uuid4()
    officer_dto = OfficerDto(id=uuid.uuid4(), user_id=officer_user_id, employee_code="EMP-1")
    apps = FakeApps(app)
    use_case = RecordOfficerDecision(
        apps,
        FakeOfficers({officer_user_id: officer_dto}),
        RecordingDecisions(),
        FakeRiskScores(None),
        RecordingAuditLog(),
    )

    await use_case.execute(
        RecordDecisionCommand(
            app.id, DecisionType.REQUEST_MORE_INFO, "Please re-upload the video."
        ),
        officer_user_id,
    )

    assert app.status is ApplicationStatus.MORE_INFO_REQUESTED
    # mark_decided is False for a non-terminal outcome.
    assert apps.status_changes[-1] == (ApplicationStatus.MORE_INFO_REQUESTED, False, False)


async def test_record_decision_rejects_empty_reason() -> None:
    app = _app()
    officer_user_id = uuid.uuid4()
    use_case = RecordOfficerDecision(
        FakeApps(app),
        FakeOfficers({officer_user_id: OfficerDto(uuid.uuid4(), officer_user_id, "EMP-1")}),
        RecordingDecisions(),
        FakeRiskScores(None),
        RecordingAuditLog(),
    )
    with pytest.raises(ValidationError):
        await use_case.execute(
            RecordDecisionCommand(app.id, DecisionType.APPROVE, "   "), officer_user_id
        )


async def test_record_decision_rejects_wrong_status() -> None:
    app = _app(status=ApplicationStatus.DRAFT)
    officer_user_id = uuid.uuid4()
    use_case = RecordOfficerDecision(
        FakeApps(app),
        FakeOfficers({officer_user_id: OfficerDto(uuid.uuid4(), officer_user_id, "EMP-1")}),
        RecordingDecisions(),
        FakeRiskScores(None),
        RecordingAuditLog(),
    )
    with pytest.raises(InvalidStateTransitionError):
        await use_case.execute(
            RecordDecisionCommand(app.id, DecisionType.APPROVE, "ok"), officer_user_id
        )


async def test_record_decision_requires_officer_profile() -> None:
    app = _app()
    officer_user_id = uuid.uuid4()  # no matching OfficerDto
    use_case = RecordOfficerDecision(
        FakeApps(app),
        FakeOfficers({}),
        RecordingDecisions(),
        FakeRiskScores(None),
        RecordingAuditLog(),
    )
    with pytest.raises(NotFoundError):
        await use_case.execute(
            RecordDecisionCommand(app.id, DecisionType.APPROVE, "ok"), officer_user_id
        )


# --- GetAuditTrail ---
async def test_audit_trail_lists_entries_for_application() -> None:
    app = _app()
    audit = RecordingAuditLog()
    await audit.log(
        action=AuditAction.OFFICER_DECISION,
        actor_user_id=uuid.uuid4(),
        application_id=app.id,
        metadata={"decision": "approve"},
    )
    entries = await GetAuditTrail(FakeApps(app), audit).execute(
        app.id, uuid.uuid4(), UserRole.AUDITOR
    )
    assert len(entries) == 1
    assert entries[0].action == "officer_decision"


async def test_audit_trail_denies_applicant() -> None:
    app = _app()
    with pytest.raises(NotFoundError):
        await GetAuditTrail(FakeApps(app), RecordingAuditLog()).execute(
            app.id, app.applicant_id, UserRole.APPLICANT
        )
