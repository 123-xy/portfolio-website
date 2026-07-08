from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.repositories.officer_repository import OfficerDto, OfficerRepository
from app.infrastructure.db.models.officer import Officer as OfficerModel


class SqlAlchemyOfficerRepository(OfficerRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_user_id(self, user_id: uuid.UUID) -> OfficerDto | None:
        result = await self._session.execute(
            select(OfficerModel).where(OfficerModel.user_id == user_id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return OfficerDto(id=model.id, user_id=model.user_id, employee_code=model.employee_code)
