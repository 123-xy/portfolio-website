from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from app.application.dto.officer_review import OfficerDecisionDto
from app.domain.value_objects.enums import DecisionType


class OfficerDecisionRepository(ABC):
    @abstractmethod
    async def record(
        self,
        *,
        application_id: uuid.UUID,
        officer_id: uuid.UUID,
        decision: DecisionType,
        reason: str,
        risk_score_id: uuid.UUID | None,
    ) -> OfficerDecisionDto:
        """Append-only: never updates a prior decision, always inserts a new
        row (a reversal is a new decision, preserving full history)."""
        ...

    @abstractmethod
    async def list_for_application(self, application_id: uuid.UUID) -> list[OfficerDecisionDto]: ...
