from __future__ import annotations

import uuid

from app.application.dto.officer_review import OfficerDecisionDto, RecordDecisionCommand
from app.application.ports.repositories.application_repository import ApplicationRepository
from app.application.ports.repositories.audit_log_repository import AuditLogRepository
from app.application.ports.repositories.officer_decision_repository import (
    OfficerDecisionRepository,
)
from app.application.ports.repositories.officer_repository import OfficerRepository
from app.application.ports.repositories.risk_score_repository import RiskScoreRepository
from app.domain.exceptions import InvalidStateTransitionError, NotFoundError, ValidationError
from app.domain.value_objects.enums import ApplicationStatus, AuditAction, DecisionType

_NEW_STATUS: dict[DecisionType, ApplicationStatus] = {
    DecisionType.APPROVE: ApplicationStatus.APPROVED,
    DecisionType.REJECT: ApplicationStatus.REJECTED,
    DecisionType.REQUEST_MORE_INFO: ApplicationStatus.MORE_INFO_REQUESTED,
}
# Only "request more info" leaves the application re-actionable by the
# applicant; approve/reject are terminal outcomes.
_TERMINAL = {DecisionType.APPROVE, DecisionType.REJECT}


class RecordOfficerDecision:
    """Records an officer's approve/reject/request-more-info decision.

    Requires a non-empty reason (enforced by the schema and again here), a
    valid officer profile for the acting user, and an application actually
    awaiting review — an officer cannot decide on a draft or already-decided
    application. Every decision is also written to the audit trail.
    """

    def __init__(
        self,
        applications: ApplicationRepository,
        officers: OfficerRepository,
        decisions: OfficerDecisionRepository,
        risk_scores: RiskScoreRepository,
        audit_log: AuditLogRepository,
    ) -> None:
        self._applications = applications
        self._officers = officers
        self._decisions = decisions
        self._risk_scores = risk_scores
        self._audit_log = audit_log

    async def execute(
        self, command: RecordDecisionCommand, officer_user_id: uuid.UUID
    ) -> OfficerDecisionDto:
        reason = command.reason.strip()
        if not reason:
            raise ValidationError("A reason is required for every decision.")

        app = await self._applications.get_by_id(command.application_id)
        if app is None:
            raise NotFoundError("Application not found.")
        if app.status is not ApplicationStatus.PENDING_REVIEW:
            raise InvalidStateTransitionError(
                "This application is not currently awaiting officer review."
            )

        officer = await self._officers.get_by_user_id(officer_user_id)
        if officer is None:
            raise NotFoundError("No officer profile is associated with this account.")

        current_risk = await self._risk_scores.get_current(app.id)

        decision = await self._decisions.record(
            application_id=app.id,
            officer_id=officer.id,
            decision=command.decision,
            reason=reason,
            risk_score_id=current_risk.id if current_risk else None,
        )

        new_status = _NEW_STATUS[command.decision]
        await self._applications.set_status(
            app.id, new_status, mark_decided=command.decision in _TERMINAL
        )

        await self._audit_log.log(
            action=AuditAction.OFFICER_DECISION,
            actor_user_id=officer_user_id,
            application_id=app.id,
            target_type="officer_decision",
            target_id=decision.id,
            metadata={"decision": command.decision.value, "reason": reason},
        )
        return decision
