from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.application.ports.repositories.application_repository import ApplicationRepository
from app.application.use_cases.applications.access import authorize_owner
from app.domain.entities.application import Application
from app.domain.exceptions import InvalidStateTransitionError, NotFoundError, ValidationError
from app.domain.value_objects.enums import ApplicationStatus, ArtifactKind, UserRole
from app.domain.value_objects.upload_policy import REQUIRED_KINDS

_SUBMITTABLE_STATUSES = {ApplicationStatus.DRAFT, ApplicationStatus.MORE_INFO_REQUESTED}
# Artifact statuses that count as a present upload for submission.
_PRESENT_STATUSES = {"uploaded", "ingested", "validated"}


class SubmitApplication:
    """Transition a draft application to `submitted` once all required artifacts
    are present, making it eligible for the AI verification pipeline.

    The pipeline is enqueued here in Phase 9; for now the transition is the
    contract the pipeline will hook onto.
    """

    def __init__(self, applications: ApplicationRepository) -> None:
        self._applications = applications

    async def execute(
        self, application_id: uuid.UUID, requester_id: uuid.UUID, role: UserRole
    ) -> Application:
        app = await self._applications.get_by_id(application_id)
        if app is None:
            raise NotFoundError("Application not found.")
        authorize_owner(app, requester_id, role)

        if app.status not in _SUBMITTABLE_STATUSES:
            raise InvalidStateTransitionError("Application has already been submitted.")

        present = {
            ArtifactKind(a.kind) for a in app.artifacts if a.status in _PRESENT_STATUSES
        }
        missing = REQUIRED_KINDS - present
        if missing:
            names = ", ".join(sorted(k.value for k in missing))
            raise ValidationError(f"Missing required uploads: {names}.")

        await self._applications.set_status(
            app.id, ApplicationStatus.SUBMITTED, mark_submitted=True
        )
        # Reflect the persisted transition on the returned entity.
        app.status = ApplicationStatus.SUBMITTED
        app.submitted_at = datetime.now(UTC)
        # Phase 9 enqueues the verification pipeline for app.id here.
        return app
