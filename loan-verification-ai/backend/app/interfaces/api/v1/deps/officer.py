from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from app.application.ports.repositories.audit_log_repository import AuditLogRepository
from app.application.ports.repositories.officer_decision_repository import (
    OfficerDecisionRepository,
)
from app.application.ports.repositories.officer_repository import OfficerRepository
from app.application.ports.repositories.verification_result_repository import (
    VerificationResultRepository,
)
from app.application.use_cases.officer_review.get_artifact_download_url import (
    GetArtifactDownloadUrl,
)
from app.application.use_cases.officer_review.get_audit_trail import GetAuditTrail
from app.application.use_cases.officer_review.get_verification_details import (
    GetVerificationDetails,
)
from app.application.use_cases.officer_review.record_officer_decision import (
    RecordOfficerDecision,
)
from app.infrastructure.db.repositories.audit_log_repository import SqlAlchemyAuditLogRepository
from app.infrastructure.db.repositories.officer_decision_repository import (
    SqlAlchemyOfficerDecisionRepository,
)
from app.infrastructure.db.repositories.officer_repository import SqlAlchemyOfficerRepository
from app.infrastructure.db.repositories.verification_result_repository import (
    SqlAlchemyVerificationResultRepository,
)
from app.interfaces.api.v1.deps.applications import AppRepoDep, RiskScoreRepoDep, StorageDep
from app.interfaces.api.v1.deps.auth import SessionDep


def get_verification_result_repository(session: SessionDep) -> VerificationResultRepository:
    return SqlAlchemyVerificationResultRepository(session)


def get_officer_repository(session: SessionDep) -> OfficerRepository:
    return SqlAlchemyOfficerRepository(session)


def get_officer_decision_repository(session: SessionDep) -> OfficerDecisionRepository:
    return SqlAlchemyOfficerDecisionRepository(session)


def get_audit_log_repository(session: SessionDep) -> AuditLogRepository:
    return SqlAlchemyAuditLogRepository(session)


VerificationResultRepoDep = Annotated[
    VerificationResultRepository, Depends(get_verification_result_repository)
]
OfficerRepoDep = Annotated[OfficerRepository, Depends(get_officer_repository)]
OfficerDecisionRepoDep = Annotated[
    OfficerDecisionRepository, Depends(get_officer_decision_repository)
]
AuditLogRepoDep = Annotated[AuditLogRepository, Depends(get_audit_log_repository)]


def get_get_verification_details(
    applications: AppRepoDep, results: VerificationResultRepoDep
) -> GetVerificationDetails:
    return GetVerificationDetails(applications, results)


def get_get_artifact_download_url(
    applications: AppRepoDep, storage: StorageDep, audit_log: AuditLogRepoDep
) -> GetArtifactDownloadUrl:
    return GetArtifactDownloadUrl(applications, storage, audit_log)


def get_record_officer_decision(
    applications: AppRepoDep,
    officers: OfficerRepoDep,
    decisions: OfficerDecisionRepoDep,
    risk_scores: RiskScoreRepoDep,
    audit_log: AuditLogRepoDep,
) -> RecordOfficerDecision:
    return RecordOfficerDecision(applications, officers, decisions, risk_scores, audit_log)


def get_get_audit_trail(applications: AppRepoDep, audit_log: AuditLogRepoDep) -> GetAuditTrail:
    return GetAuditTrail(applications, audit_log)
