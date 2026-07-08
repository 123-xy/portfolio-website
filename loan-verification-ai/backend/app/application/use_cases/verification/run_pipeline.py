from __future__ import annotations

import logging
import uuid

from app.application.dto.verification import PipelineContext, StageOutcome
from app.application.ports.repositories.application_repository import ApplicationRepository
from app.application.ports.repositories.verification_result_repository import (
    VerificationResultRepository,
)
from app.application.ports.services.pipeline import StageRunner
from app.domain.value_objects.enums import ApplicationStatus, StageStatus, VerificationStage

logger = logging.getLogger("app.pipeline")

# Perception + analysis stages run in Phase 9. Risk scoring (the final stage in
# the enum) is added by the risk engine in Phase 10.
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
    ) -> None:
        self._applications = applications
        self._results = results
        self._stage_runner = stage_runner

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

        # Perception complete. Phase 10 inserts risk scoring before this point;
        # for now the application is ready for officer review.
        await self._applications.set_status(app.id, ApplicationStatus.PENDING_REVIEW)
        logger.info("pipeline_completed", extra={"application_id": str(app.id)})
