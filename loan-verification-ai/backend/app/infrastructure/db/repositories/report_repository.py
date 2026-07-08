from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.reports import ReportDto
from app.application.ports.repositories.report_repository import ReportRepository
from app.domain.value_objects.enums import ReportFormat
from app.infrastructure.db.models.report import Report as ReportModel


def _to_dto(model: ReportModel) -> ReportDto:
    return ReportDto(
        id=model.id,
        application_id=model.application_id,
        format=model.format,
        storage_key=model.storage_key,
        version=model.version,
        created_at=model.created_at,
    )


class SqlAlchemyReportRepository(ReportRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def next_version(self, application_id: uuid.UUID | None, format: ReportFormat) -> int:
        conditions = [ReportModel.format == format]
        if application_id is None:
            conditions.append(ReportModel.application_id.is_(None))
        else:
            conditions.append(ReportModel.application_id == application_id)
        result = await self._session.execute(
            select(func.coalesce(func.max(ReportModel.version), 0)).where(*conditions)
        )
        return int(result.scalar_one()) + 1

    async def create(
        self,
        *,
        application_id: uuid.UUID | None,
        format: ReportFormat,
        storage_key: str,
        generated_by: uuid.UUID,
        version: int,
    ) -> ReportDto:
        model = ReportModel(
            application_id=application_id,
            format=format,
            storage_key=storage_key,
            generated_by=generated_by,
            version=version,
        )
        self._session.add(model)
        await self._session.flush()
        return _to_dto(model)

    async def get_by_id(self, report_id: uuid.UUID) -> ReportDto | None:
        model = await self._session.get(ReportModel, report_id)
        return _to_dto(model) if model else None
