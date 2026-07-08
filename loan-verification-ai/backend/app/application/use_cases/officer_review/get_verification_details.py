from __future__ import annotations

import uuid

from app.application.dto.officer_review import VerificationDetails
from app.application.ports.repositories.application_repository import ApplicationRepository
from app.application.ports.repositories.verification_result_repository import (
    VerificationResultRepository,
)
from app.application.use_cases.applications.access import authorize_staff
from app.application.use_cases.officer_review.verification_mapping import (
    build_verification_details,
)
from app.domain.exceptions import NotFoundError
from app.domain.value_objects.enums import UserRole


class GetVerificationDetails:
    """Assembles the officer's evidence pack — transcript, consent/intent
    findings, fraud signals, face match — from the pipeline's latest per-stage
    results. Staff-only: this is the reviewer's detail view, not the
    applicant's."""

    def __init__(
        self, applications: ApplicationRepository, results: VerificationResultRepository
    ) -> None:
        self._applications = applications
        self._results = results

    async def execute(
        self, application_id: uuid.UUID, requester_id: uuid.UUID, role: UserRole
    ) -> VerificationDetails:
        app = await self._applications.get_by_id(application_id)
        if app is None:
            raise NotFoundError("Application not found.")
        authorize_staff(role)

        scalars = await self._results.latest_scalars(application_id)
        return build_verification_details(scalars)
