from __future__ import annotations

import uuid

from app.domain.entities.application import Application
from app.domain.exceptions import NotFoundError
from app.domain.value_objects.enums import UserRole

_STAFF_ROLES = {UserRole.OFFICER, UserRole.AUDITOR, UserRole.ADMIN}


def authorize_view(app: Application, requester_id: uuid.UUID, role: UserRole) -> None:
    """Staff may view any application; an applicant only their own. A denied
    view raises NotFound (not Forbidden) so the API never confirms the existence
    of another applicant's application."""
    if role in _STAFF_ROLES or app.applicant_id == requester_id:
        return
    raise NotFoundError("Application not found.")


def authorize_owner(app: Application, requester_id: uuid.UUID, role: UserRole) -> None:
    """Mutating an application's artifacts / submitting it is reserved to the
    owning applicant — staff review but do not upload on an applicant's behalf."""
    if app.applicant_id == requester_id:
        return
    raise NotFoundError("Application not found.")


def authorize_staff(role: UserRole) -> None:
    """Officer-review evidence (transcript, fraud/intent detail, audit trail)
    is staff-only — narrower than authorize_view, which also lets an
    applicant see their own application."""
    if role not in _STAFF_ROLES:
        raise NotFoundError("Application not found.")
