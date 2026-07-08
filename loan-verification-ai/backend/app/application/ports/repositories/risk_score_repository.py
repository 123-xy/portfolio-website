from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from app.application.dto.risk import RiskAssessment, RiskScoreDto


class RiskScoreRepository(ABC):
    @abstractmethod
    async def record(
        self,
        *,
        application_id: uuid.UUID,
        assessment: RiskAssessment,
        weights: dict[str, float],
        config_version: int,
    ) -> None:
        """Persist a new current score, superseding any prior current score for
        this application (the `is_current` invariant is maintained here)."""
        ...

    @abstractmethod
    async def get_current(self, application_id: uuid.UUID) -> RiskScoreDto | None: ...

    @abstractmethod
    async def get_current_batch(
        self, application_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, RiskScoreDto]: ...
