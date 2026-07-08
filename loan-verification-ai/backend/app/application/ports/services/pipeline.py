from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from app.application.dto.verification import PipelineContext, StageOutcome
from app.domain.value_objects.enums import VerificationStage


class StageRunner(ABC):
    """Runs a single verification stage. Implemented in infrastructure over the
    ai-services library (deterministic default) or real model backends."""

    @abstractmethod
    async def run(self, stage: VerificationStage, context: PipelineContext) -> StageOutcome: ...


class PipelineDispatcher(ABC):
    """Enqueues the verification pipeline for an application (Celery in prod)."""

    @abstractmethod
    def dispatch(self, application_id: uuid.UUID) -> None: ...
