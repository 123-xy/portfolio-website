from __future__ import annotations

import uuid

from app.application.dto.applications import ApplicationWithRisk
from app.application.ports.repositories.application_repository import ApplicationRepository
from app.application.ports.repositories.risk_score_repository import RiskScoreRepository
from app.application.use_cases.applications.access import authorize_view
from app.domain.exceptions import NotFoundError
from app.domain.value_objects.enums import UserRole


class ListApplications:
    """List applications appropriate to the requester: an applicant sees their
    own; staff see the review queue. Each is paired with its current risk
    score (if scoring has completed) in a single batched lookup."""

    def __init__(
        self, applications: ApplicationRepository, risk_scores: RiskScoreRepository
    ) -> None:
        self._applications = applications
        self._risk_scores = risk_scores

    async def execute(self, requester_id: uuid.UUID, role: UserRole) -> list[ApplicationWithRisk]:
        if role is UserRole.APPLICANT:
            apps = await self._applications.list_for_applicant(requester_id)
        else:
            apps = await self._applications.list_for_review()

        risk_by_app = await self._risk_scores.get_current_batch([a.id for a in apps])
        return [ApplicationWithRisk(application=a, risk=risk_by_app.get(a.id)) for a in apps]


class GetApplication:
    """Fetch a single application with its current risk score, enforcing view
    authorization."""

    def __init__(
        self, applications: ApplicationRepository, risk_scores: RiskScoreRepository
    ) -> None:
        self._applications = applications
        self._risk_scores = risk_scores

    async def execute(
        self, application_id: uuid.UUID, requester_id: uuid.UUID, role: UserRole
    ) -> ApplicationWithRisk:
        app = await self._applications.get_by_id(application_id)
        if app is None:
            raise NotFoundError("Application not found.")
        authorize_view(app, requester_id, role)
        risk = await self._risk_scores.get_current(app.id)
        return ApplicationWithRisk(application=app, risk=risk)
