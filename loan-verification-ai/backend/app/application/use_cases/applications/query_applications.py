from __future__ import annotations

import uuid

from app.application.ports.repositories.application_repository import ApplicationRepository
from app.application.use_cases.applications.access import authorize_view
from app.domain.entities.application import Application
from app.domain.exceptions import NotFoundError
from app.domain.value_objects.enums import UserRole


class ListApplications:
    """List applications appropriate to the requester: an applicant sees their
    own; staff see the review queue."""

    def __init__(self, applications: ApplicationRepository) -> None:
        self._applications = applications

    async def execute(self, requester_id: uuid.UUID, role: UserRole) -> list[Application]:
        if role is UserRole.APPLICANT:
            return await self._applications.list_for_applicant(requester_id)
        return await self._applications.list_for_review()


class GetApplication:
    """Fetch a single application, enforcing view authorization."""

    def __init__(self, applications: ApplicationRepository) -> None:
        self._applications = applications

    async def execute(
        self, application_id: uuid.UUID, requester_id: uuid.UUID, role: UserRole
    ) -> Application:
        app = await self._applications.get_by_id(application_id)
        if app is None:
            raise NotFoundError("Application not found.")
        authorize_view(app, requester_id, role)
        return app
