from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from app.application.dto.officer_review import RecordDecisionCommand
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
from app.domain.value_objects.enums import UserRole
from app.interfaces.api.v1.deps.auth import CurrentUser, require_role
from app.interfaces.api.v1.deps.officer import (
    get_get_artifact_download_url,
    get_get_audit_trail,
    get_get_verification_details,
    get_record_officer_decision,
)
from app.interfaces.api.v1.schemas.officer import (
    ArtifactDownloadResponse,
    AuditEntryResponse,
    DecisionRequest,
    DecisionResponse,
    VerificationDetailsResponse,
)

# Nested under /applications to reuse the existing resource hierarchy and
# access-control helpers; a separate tag keeps it grouped as its own feature
# area (the officer review dashboard) in the OpenAPI docs.
router = APIRouter(prefix="/applications", tags=["officer"])

StaffUser = Annotated[
    object, Depends(require_role(UserRole.OFFICER, UserRole.AUDITOR, UserRole.ADMIN))
]


@router.get(
    "/{application_id}/verification",
    response_model=VerificationDetailsResponse,
    summary="Evidence pack: transcript, consent/intent findings, fraud signals",
)
async def get_verification_details(
    application_id: uuid.UUID,
    current_user: CurrentUser,
    use_case: Annotated[GetVerificationDetails, Depends(get_get_verification_details)],
) -> VerificationDetailsResponse:
    details = await use_case.execute(application_id, current_user.id, current_user.role)
    return VerificationDetailsResponse(**details.__dict__)


@router.get(
    "/{application_id}/artifacts/{artifact_id}/download",
    response_model=ArtifactDownloadResponse,
    summary="Presigned URL to view a photo/video artifact",
)
async def get_artifact_download_url(
    application_id: uuid.UUID,
    artifact_id: uuid.UUID,
    current_user: CurrentUser,
    use_case: Annotated[GetArtifactDownloadUrl, Depends(get_get_artifact_download_url)],
) -> ArtifactDownloadResponse:
    url = await use_case.execute(
        application_id, artifact_id, current_user.id, current_user.role
    )
    return ArtifactDownloadResponse(download_url=url)


@router.post(
    "/{application_id}/decision",
    response_model=DecisionResponse,
    summary="Approve / reject / request more info",
)
async def record_decision(
    application_id: uuid.UUID,
    body: DecisionRequest,
    current_user: CurrentUser,
    _staff: Annotated[
        object, Depends(require_role(UserRole.OFFICER))
    ],
    use_case: Annotated[RecordOfficerDecision, Depends(get_record_officer_decision)],
) -> DecisionResponse:
    decision = await use_case.execute(
        RecordDecisionCommand(
            application_id=application_id, decision=body.decision, reason=body.reason
        ),
        current_user.id,
    )
    return DecisionResponse(
        id=decision.id,
        decision=decision.decision,
        reason=decision.reason,
        created_at=decision.created_at,
    )


@router.get(
    "/{application_id}/audit",
    response_model=list[AuditEntryResponse],
    summary="Audit trail for an application",
)
async def get_audit_trail(
    application_id: uuid.UUID,
    current_user: CurrentUser,
    use_case: Annotated[GetAuditTrail, Depends(get_get_audit_trail)],
) -> list[AuditEntryResponse]:
    entries = await use_case.execute(application_id, current_user.id, current_user.role)
    return [
        AuditEntryResponse(
            id=e.id,
            action=e.action,
            actor_user_id=e.actor_user_id,
            is_system=e.is_system,
            target_type=e.target_type,
            target_id=e.target_id,
            metadata=e.metadata,
            created_at=e.created_at,
        )
        for e in entries
    ]
