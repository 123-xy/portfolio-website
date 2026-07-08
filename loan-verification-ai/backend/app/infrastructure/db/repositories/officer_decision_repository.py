from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.officer_review import OfficerDecisionDto
from app.application.ports.repositories.officer_decision_repository import (
    OfficerDecisionRepository,
)
from app.domain.value_objects.enums import DecisionType
from app.infrastructure.db.models.officer_decision import OfficerDecision as OfficerDecisionModel


def _to_dto(model: OfficerDecisionModel) -> OfficerDecisionDto:
    return OfficerDecisionDto(
        id=model.id, decision=model.decision, reason=model.reason, created_at=model.created_at
    )


class SqlAlchemyOfficerDecisionRepository(OfficerDecisionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record(
        self,
        *,
        application_id: uuid.UUID,
        officer_id: uuid.UUID,
        decision: DecisionType,
        reason: str,
        risk_score_id: uuid.UUID | None,
    ) -> OfficerDecisionDto:
        model = OfficerDecisionModel(
            application_id=application_id,
            officer_id=officer_id,
            decision=decision,
            reason=reason,
            risk_score_id=risk_score_id,
        )
        self._session.add(model)
        await self._session.flush()
        return _to_dto(model)

    async def list_for_application(self, application_id: uuid.UUID) -> list[OfficerDecisionDto]:
        result = await self._session.execute(
            select(OfficerDecisionModel)
            .where(OfficerDecisionModel.application_id == application_id)
            .order_by(OfficerDecisionModel.created_at.desc())
        )
        return [_to_dto(m) for m in result.scalars().all()]
