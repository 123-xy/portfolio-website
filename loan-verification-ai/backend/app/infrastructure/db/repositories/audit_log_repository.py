from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.officer_review import AuditEntryDto
from app.application.ports.repositories.audit_log_repository import AuditLogRepository
from app.domain.value_objects.enums import AuditAction
from app.infrastructure.db.models.audit_log import AuditLog as AuditLogModel


def _to_dto(model: AuditLogModel) -> AuditEntryDto:
    return AuditEntryDto(
        id=model.id,
        action=model.action.value,
        actor_user_id=model.actor_user_id,
        is_system=model.is_system,
        target_type=model.target_type,
        target_id=model.target_id,
        metadata=model.audit_metadata,
        created_at=model.created_at,
    )


class SqlAlchemyAuditLogRepository(AuditLogRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def log(
        self,
        *,
        action: AuditAction,
        actor_user_id: uuid.UUID | None,
        application_id: uuid.UUID | None,
        target_type: str | None = None,
        target_id: uuid.UUID | None = None,
        metadata: dict[str, object] | None = None,
    ) -> None:
        self._session.add(
            AuditLogModel(
                action=action,
                actor_user_id=actor_user_id,
                is_system=actor_user_id is None,
                application_id=application_id,
                target_type=target_type,
                target_id=target_id,
                audit_metadata=metadata,
            )
        )
        await self._session.flush()

    async def list_for_application(self, application_id: uuid.UUID) -> list[AuditEntryDto]:
        result = await self._session.execute(
            select(AuditLogModel)
            .where(AuditLogModel.application_id == application_id)
            .order_by(AuditLogModel.created_at.desc())
        )
        return [_to_dto(m) for m in result.scalars().all()]
