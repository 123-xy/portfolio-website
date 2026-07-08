from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from app.application.dto.verification import StageOutcome
from app.domain.value_objects.enums import VerificationStage


class VerificationResultRepository(ABC):
    """Persistence port for per-stage verification results (attempt-versioned)."""

    @abstractmethod
    async def next_attempt(self, application_id: uuid.UUID, stage: VerificationStage) -> int:
        """The next attempt number for this application/stage (1-based)."""
        ...

    @abstractmethod
    async def record(
        self,
        *,
        application_id: uuid.UUID,
        stage: VerificationStage,
        attempt: int,
        outcome: StageOutcome,
    ) -> None: ...

    @abstractmethod
    async def latest_scalars(
        self, application_id: uuid.UUID
    ) -> dict[VerificationStage, dict[str, object]]:
        """Latest completed scalar signals per stage (for the risk engine and
        the officer view)."""
        ...
