from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from app.application.dto.officer_review import AuditEntryDto
from app.domain.value_objects.enums import AuditAction


class AuditLogRepository(ABC):
    @abstractmethod
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
        """Append a tamper-evident audit entry. Never updated or deleted by
        application code."""
        ...

    @abstractmethod
    async def list_for_application(self, application_id: uuid.UUID) -> list[AuditEntryDto]: ...
