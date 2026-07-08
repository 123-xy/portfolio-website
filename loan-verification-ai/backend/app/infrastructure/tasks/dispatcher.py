from __future__ import annotations

import uuid

from app.application.ports.services.pipeline import PipelineDispatcher


class CeleryPipelineDispatcher(PipelineDispatcher):
    """Enqueues the verification pipeline on Celery.

    A short countdown lets the submitting request's transaction commit before
    the worker reads the application, avoiding a read-before-commit race.
    """

    def __init__(self, countdown_seconds: int = 2) -> None:
        self._countdown = countdown_seconds

    def dispatch(self, application_id: uuid.UUID) -> None:
        # Imported lazily so importing this module doesn't require a broker.
        from app.infrastructure.tasks.pipeline_tasks import run_verification_pipeline

        run_verification_pipeline.apply_async(
            args=[str(application_id)], countdown=self._countdown
        )
