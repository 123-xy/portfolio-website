from __future__ import annotations

import logging
import uuid

from app.application.dto.verification import PipelineContext, StageOutcome
from app.application.ports.repositories.application_repository import ApplicationRepository
from app.application.ports.repositories.risk_engine_config_repository import (
    RiskEngineConfigRepository,
)
from app.application.ports.repositories.risk_score_repository import RiskScoreRepository
from app.application.ports.repositories.verification_result_repository import (
    VerificationResultRepository,
)
from app.application.ports.services.pipeline import StageRunner
from app.application.ports.services.risk_scoring import RiskScoringService
from app.application.use_cases.verification.risk_inputs import build_risk_inputs
from app.domain.value_objects.enums import ApplicationStatus, StageStatus, VerificationStage

logger = logging.getLogger("app.pipeline")

# Perception + analysis stages, run per-artifact via the StageRunner. Risk
# scoring is a distinct final step (see _score_risk) — it aggregates every
# other stage's output plus admin config rather than calling a single AI
# service, so it does not fit the generic StageRunner shape.
PIPELINE_STAGES: list[VerificationStage] = [
    VerificationStage.INGEST,
    VerificationStage.FRAME_EXTRACTION,
    VerificationStage.FACE_DETECTION,
    VerificationStage.FACE_EMBEDDING,
    VerificationStage.FACE_MATCH,
    VerificationStage.AUDIO_EXTRACTION,
    VerificationStage.TRANSCRIPTION,
    VerificationStage.CONSENT_DETECTION,
    VerificationStage.INTENT_ANALYSIS,
    VerificationStage.FRAUD_CHECK,
]

# Statuses from which a pipeline run is valid (submit, or a retry of a stuck/failed run).
_RUNNABLE = {
    ApplicationStatus.SUBMITTED,
    ApplicationStatus.PROCESSING,
    ApplicationStatus.NEEDS_ATTENTION,
}


class RunVerificationPipeline:
    """Orchestrates the verification stages for one application.

    Each stage is attempt-versioned and persisted independently, so a run is
    resumable/replayable and every stage outcome is auditable. A failed stage
    routes the application to `needs_attention` for ops rather than silently
    dropping it.
    """

    def __init__(
        self,
        applications: ApplicationRepository,
        results: VerificationResultRepository,
        stage_runner: StageRunner,
        risk_config: RiskEngineConfigRepository,
        risk_scores: RiskScoreRepository,
        risk_scoring: RiskScoringService,
    ) -> None:
        self._applications = applications
        self._results = results
        self._stage_runner = stage_runner
        self._risk_config = risk_config
        self._risk_scores = risk_scores
        self._risk_scoring = risk_scoring

    async def execute(self, application_id: uuid.UUID) -> None:
        app = await self._applications.get_by_id(application_id)
        if app is None:
            logger.warning(
                "pipeline_missing_application",
                extra={"application_id": str(application_id)},
            )
            return
        if app.status not in _RUNNABLE:
            logger.info(
                "pipeline_skipped_wrong_status",
                extra={"application_id": str(application_id), "status": app.status.value},
            )
            return

        await self._applications.set_status(app.id, ApplicationStatus.PROCESSING)
        context = PipelineContext(application=app)

        for stage in PIPELINE_STAGES:
            attempt = await self._results.next_attempt(app.id, stage)
            try:
                outcome = await self._stage_runner.run(stage, context)
            except Exception as exc:  # noqa: BLE001 — a stage failure must not crash the run
                logger.exception("pipeline_stage_error", extra={"stage": stage.value})
                outcome = StageOutcome.failed(f"{type(exc).__name__}: {exc}")

            await self._results.record(
                application_id=app.id, stage=stage, attempt=attempt, outcome=outcome
            )

            if outcome.status is StageStatus.FAILED:
                await self._applications.set_status(app.id, ApplicationStatus.NEEDS_ATTENTION)
                logger.warning(
                    "pipeline_failed",
                    extra={"application_id": str(app.id), "stage": stage.value},
                )
                return

        # Perception/analysis complete — aggregate into a risk score.
        scored = await self._score_risk(app.id)
        if not scored:
            await self._applications.set_status(app.id, ApplicationStatus.NEEDS_ATTENTION)
            logger.warning(
                "pipeline_failed",
                extra={"application_id": str(app.id), "stage": "risk_scoring"},
            )
            return

        await self._applications.set_status(app.id, ApplicationStatus.PENDING_REVIEW)
        logger.info("pipeline_completed", extra={"application_id": str(app.id)})

    async def _score_risk(self, application_id: uuid.UUID) -> bool:
        """Aggregate every stage's latest scalars into a risk score and persist
        both the risk_scores row and a corresponding verification_results row
        (stage=risk_scoring) for a complete, auditable pipeline history."""
        stage = VerificationStage.RISK_SCORING
        attempt = await self._results.next_attempt(application_id, stage)
        try:
            scalars = await self._results.latest_scalars(application_id)
            config = await self._risk_config.get_active()
            inputs = build_risk_inputs(scalars)
            assessment = self._risk_scoring.score(inputs, config.weights, config.thresholds)
            await self._risk_scores.record(
                application_id=application_id,
                assessment=assessment,
                weights=config.weights,
                config_version=config.version,
            )
        except Exception as exc:  # noqa: BLE001 — a failure here must not crash the run
            logger.exception("risk_scoring_error")
            await self._results.record(
                application_id=application_id,
                stage=stage,
                attempt=attempt,
                outcome=StageOutcome.failed(f"{type(exc).__name__}: {exc}"),
            )
            return False

        await self._results.record(
            application_id=application_id,
            stage=stage,
            attempt=attempt,
            outcome=StageOutcome(
                status=StageStatus.COMPLETED,
                confidence=assessment.confidence,
                payload={
                    "score": assessment.score,
                    "band": assessment.band,
                    "recommendation": assessment.recommendation,
                    "component_scores": assessment.component_scores,
                    "reasons": assessment.reasons,
                },
            ),
        )
        return True
