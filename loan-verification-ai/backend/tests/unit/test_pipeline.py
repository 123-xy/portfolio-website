from __future__ import annotations

import uuid
from decimal import Decimal

from ai_services import build_consent_detector, build_face_matcher, build_intent_analyzer

from app.application.dto.risk import RiskAssessment, RiskEngineConfigDto
from app.application.dto.verification import PipelineContext, StageOutcome
from app.application.ports.repositories.application_repository import ApplicationRepository
from app.application.ports.repositories.risk_engine_config_repository import (
    RiskEngineConfigRepository,
)
from app.application.ports.repositories.risk_score_repository import RiskScoreRepository
from app.application.ports.repositories.verification_result_repository import (
    VerificationResultRepository,
)
from app.application.ports.services.object_storage import ObjectStat, ObjectStorage
from app.application.ports.services.pipeline import StageRunner
from app.application.use_cases.verification.run_pipeline import (
    PIPELINE_STAGES,
    RunVerificationPipeline,
)
from app.domain.entities.application import Application, Artifact
from app.domain.exceptions import NotFoundError
from app.domain.value_objects.enums import ApplicationStatus, StageStatus, VerificationStage
from app.infrastructure.ai.risk_scoring import AiServicesRiskScoringService
from app.infrastructure.ai.stage_runner import DeterministicStageRunner


# --- ai-services rule-based detectors (real logic) ---
def test_consent_detector_classifies_affirmative_and_refusal() -> None:
    detector = build_consent_detector()
    assert detector.detect("I agree and I give my full consent").status == "explicit_yes"
    assert detector.detect("I do not consent to this").status == "explicit_no"
    assert detector.detect("Um, I think so, I suppose").status == "ambiguous"
    assert detector.detect("The weather is nice today").status == "not_detected"


def test_intent_analyzer_detects_alignment_and_coercion() -> None:
    analyzer = build_intent_analyzer()
    aligned = analyzer.analyze("I am willing to be a co-applicant for this loan")
    assert aligned.aligned is True
    coerced = analyzer.analyze("I was told to say I agree to the loan")
    assert coerced.aligned is False


def test_face_matcher_is_deterministic_and_bounded() -> None:
    matcher = build_face_matcher()
    a = matcher.match("photo-seed", "video-seed")
    b = matcher.match("photo-seed", "video-seed")
    assert a.similarity == b.similarity
    assert 0.0 <= a.similarity <= 1.0


# --- orchestrator with fakes ---
class FakeApps(ApplicationRepository):
    def __init__(self, app: Application) -> None:
        self._app = app
        self.status_changes: list[ApplicationStatus] = []

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
        self.status_changes.append(status)


class RecordingResults(VerificationResultRepository):
    def __init__(self) -> None:
        self.recorded: list[tuple[VerificationStage, StageStatus]] = []

    async def next_attempt(self, application_id, stage) -> int:
        return 1

    async def record(self, *, application_id, stage, attempt, outcome) -> None:
        self.recorded.append((stage, outcome.status))

    async def latest_scalars(self, application_id):  # pragma: no cover
        return {}


class FakeRiskConfig(RiskEngineConfigRepository):
    def __init__(self, *, present: bool = True) -> None:
        self._present = present

    async def get_active(self) -> RiskEngineConfigDto:
        if not self._present:
            raise NotFoundError("No active risk engine configuration.")
        return RiskEngineConfigDto(
            version=1,
            weights={"face_match": 0.40, "speech": 0.20, "intent": 0.20, "fraud": 0.20},
            thresholds={"low_max": 0.33, "medium_max": 0.66},
        )


class RecordingRiskScores(RiskScoreRepository):
    def __init__(self) -> None:
        self.recorded: list[tuple[uuid.UUID, RiskAssessment, dict[str, float], int]] = []

    async def record(self, *, application_id, assessment, weights, config_version) -> None:
        self.recorded.append((application_id, assessment, weights, config_version))

    async def get_current(self, application_id):  # pragma: no cover
        return None

    async def get_current_batch(self, application_ids):  # pragma: no cover
        return {}


class AllPassRunner(StageRunner):
    async def run(self, stage, context) -> StageOutcome:
        return StageOutcome(status=StageStatus.COMPLETED)


class FailAtRunner(StageRunner):
    def __init__(self, fail_stage: VerificationStage) -> None:
        self._fail = fail_stage

    async def run(self, stage, context) -> StageOutcome:
        if stage is self._fail:
            return StageOutcome.failed("boom")
        return StageOutcome(status=StageStatus.COMPLETED)


def _app() -> Application:
    return Application(
        id=uuid.uuid4(),
        reference_no="APP-2026-000001",
        applicant_id=uuid.uuid4(),
        loan_amount=Decimal("100000"),
        status=ApplicationStatus.SUBMITTED,
    )


async def test_pipeline_runs_all_stages_scores_risk_and_marks_pending_review() -> None:
    app = _app()
    apps, results, risk_scores = FakeApps(app), RecordingResults(), RecordingRiskScores()
    await RunVerificationPipeline(
        apps,
        results,
        AllPassRunner(),
        FakeRiskConfig(),
        risk_scores,
        AiServicesRiskScoringService(),
    ).execute(app.id)

    # The 10 perception/analysis stages plus the risk_scoring step, each recorded.
    assert len(results.recorded) == len(PIPELINE_STAGES) + 1
    assert results.recorded[-1] == (VerificationStage.RISK_SCORING, StageStatus.COMPLETED)
    assert app.status is ApplicationStatus.PENDING_REVIEW
    assert ApplicationStatus.PROCESSING in apps.status_changes
    # A risk score was actually persisted, with a valid band/recommendation.
    assert len(risk_scores.recorded) == 1
    _, assessment, weights, config_version = risk_scores.recorded[0]
    assert assessment.band in {"low", "medium", "high"}
    assert config_version == 1
    assert weights["face_match"] == 0.40


async def test_pipeline_routes_to_needs_attention_on_stage_failure() -> None:
    app = _app()
    apps, results, risk_scores = FakeApps(app), RecordingResults(), RecordingRiskScores()
    await RunVerificationPipeline(
        apps,
        results,
        FailAtRunner(VerificationStage.FACE_MATCH),
        FakeRiskConfig(),
        risk_scores,
        AiServicesRiskScoringService(),
    ).execute(app.id)

    assert app.status is ApplicationStatus.NEEDS_ATTENTION
    # Stopped at the failing stage — later stages (including risk scoring) were not recorded.
    assert results.recorded[-1] == (VerificationStage.FACE_MATCH, StageStatus.FAILED)
    assert VerificationStage.TRANSCRIPTION not in [s for s, _ in results.recorded]
    assert VerificationStage.RISK_SCORING not in [s for s, _ in results.recorded]
    assert risk_scores.recorded == []


async def test_pipeline_routes_to_needs_attention_when_risk_config_missing() -> None:
    app = _app()
    apps, results, risk_scores = FakeApps(app), RecordingResults(), RecordingRiskScores()
    await RunVerificationPipeline(
        apps,
        results,
        AllPassRunner(),
        FakeRiskConfig(present=False),
        risk_scores,
        AiServicesRiskScoringService(),
    ).execute(app.id)

    assert app.status is ApplicationStatus.NEEDS_ATTENTION
    assert results.recorded[-1] == (VerificationStage.RISK_SCORING, StageStatus.FAILED)
    assert risk_scores.recorded == []


# --- deterministic stage runner end to end (no DB / no real storage) ---
class BytesStorage(ObjectStorage):
    async def ensure_bucket(self) -> None:  # pragma: no cover
        pass

    async def create_upload_url(  # pragma: no cover
        self, key, *, content_type, expires_seconds=900
    ) -> str:
        return ""

    async def create_download_url(self, key, *, expires_seconds=300) -> str:  # pragma: no cover
        return ""

    async def stat(self, key) -> ObjectStat | None:  # pragma: no cover
        return None

    async def download_bytes(self, key: str) -> bytes:
        return b"x" * 300_000

    async def upload_bytes(  # pragma: no cover
        self, key: str, data: bytes, *, content_type: str
    ) -> None:
        pass

    async def delete(self, key: str) -> None:  # pragma: no cover
        pass


class NoDupArtifacts:
    async def checksum_seen_on_other_application(self, checksum, exclude_application_id) -> bool:
        return False


def _artifact(kind: str, checksum: str) -> Artifact:
    return Artifact(
        id=uuid.uuid4(),
        application_id=uuid.uuid4(),
        kind=kind,
        status="uploaded",
        storage_key=f"k/{checksum}",
        checksum_sha256=checksum,
    )


async def test_stage_runner_produces_scalars_across_all_stages() -> None:
    app = Application(
        id=uuid.uuid4(),
        reference_no="APP-2026-000009",
        applicant_id=uuid.uuid4(),
        loan_amount=Decimal("100000"),
        status=ApplicationStatus.SUBMITTED,
        artifacts=[
            _artifact("applicant_photo", "ap"),
            _artifact("coapplicant_photo", "cp"),
            _artifact("verification_video", "vid"),
        ],
    )
    runner = DeterministicStageRunner(BytesStorage(), NoDupArtifacts())  # type: ignore[arg-type]
    context = PipelineContext(application=app)

    outcomes = {}
    for stage in PIPELINE_STAGES:
        outcome = await runner.run(stage, context)
        outcomes[stage] = outcome
        assert outcome.status is StageStatus.COMPLETED

    # Face match produced a similarity; consent produced a status.
    assert outcomes[VerificationStage.FACE_MATCH].similarity_score is not None
    assert outcomes[VerificationStage.CONSENT_DETECTION].consent is not None
    assert "fraud_score" in outcomes[VerificationStage.FRAUD_CHECK].payload
