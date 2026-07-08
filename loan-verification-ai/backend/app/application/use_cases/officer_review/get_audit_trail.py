from __future__ import annotations

import uuid

from app.application.dto.officer_review import AuditEntryDto
from app.application.ports.repositories.application_repository import ApplicationRepository
from app.application.ports.repositories.audit_log_repository import AuditLogRepository
from app.application.use_cases.applications.access import authorize_staff
from app.domain.exceptions import NotFoundError
from app.domain.value_objects.enums import UserRole


class GetAuditTrail:
    """Staff-only: the full, tamper-evident action history for an application
    (uploads, pipeline stages are not logged here — only material actions like
    decisions and artifact views — see AuditAction)."""

    def __init__(
        self, applications: ApplicationRepository, audit_log: AuditLogRepository
    ) -> None:
        self._applications = applications
        self._audit_log = audit_log

    async def execute(
        self, application_id: uuid.UUID, requester_id: uuid.UUID, role: UserRole
    ) -> list[AuditEntryDto]:
        app = await self._applications.get_by_id(application_id)
        if app is None:
            raise NotFoundError("Application not found.")
        authorize_staff(role)
        return await self._audit_log.list_for_application(application_id)
