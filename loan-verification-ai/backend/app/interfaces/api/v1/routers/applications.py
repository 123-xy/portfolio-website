from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.application.dto.applications import (
    ApplicationWithRisk,
    ConfirmUploadCommand,
    CreateApplicationCommand,
    InitUploadCommand,
)
from app.application.dto.risk import RiskScoreDto
from app.application.use_cases.applications.create_application import CreateApplication
from app.application.use_cases.applications.query_applications import (
    GetApplication,
    ListApplications,
)
from app.application.use_cases.applications.submit_application import SubmitApplication
from app.application.use_cases.applications.upload_artifact import (
    ConfirmArtifactUpload,
    InitArtifactUpload,
)
from app.domain.entities.application import Application, Artifact
from app.domain.value_objects.enums import ArtifactKind, RiskBand
from app.interfaces.api.v1.deps.applications import (
    get_confirm_upload,
    get_create_application,
    get_get_application,
    get_init_upload,
    get_list_applications,
    get_submit_application,
)
from app.interfaces.api.v1.deps.auth import CurrentUser
from app.interfaces.api.v1.schemas.applications import (
    ApplicationResponse,
    ApplicationSummaryResponse,
    ArtifactResponse,
    CoApplicantResponse,
    ConfirmUploadRequest,
    CreateApplicationRequest,
    InitUploadRequest,
    InitUploadResponse,
    RiskScoreResponse,
)

router = APIRouter(prefix="/applications", tags=["applications"])


def _artifact_response(artifact: Artifact) -> ArtifactResponse:
    return ArtifactResponse(
        id=artifact.id,
        kind=ArtifactKind(artifact.kind),
        status=artifact.status,
        mime_type=artifact.mime_type,
        size_bytes=artifact.size_bytes,
        original_filename=artifact.original_filename,
    )


def _risk_response(risk: RiskScoreDto | None) -> RiskScoreResponse | None:
    if risk is None:
        return None
    return RiskScoreResponse(
        score=risk.score,
        band=RiskBand(risk.band),
        recommendation=risk.recommendation,
        confidence=risk.confidence,
        component_scores=risk.component_scores,
        reasons=risk.reasons,
    )


def _application_response(
    app: Application, risk: RiskScoreDto | None = None
) -> ApplicationResponse:
    co = app.co_applicant
    return ApplicationResponse(
        id=app.id,
        reference_no=app.reference_no,
        loan_amount=app.loan_amount,
        loan_purpose=app.loan_purpose,
        status=app.status,
        submitted_at=app.submitted_at,
        created_at=app.created_at,
        co_applicant=(
            CoApplicantResponse(
                id=co.id,
                full_name=co.full_name,
                relationship=co.relationship_to_applicant,
                email=co.email,
                phone=co.phone,
            )
            if co
            else None
        ),
        # Rejected (superseded) artifacts are hidden from the client view.
        artifacts=[_artifact_response(a) for a in app.artifacts if a.status != "rejected"],
        risk=_risk_response(risk),
    )


def _detail_response(result: ApplicationWithRisk) -> ApplicationResponse:
    return _application_response(result.application, result.risk)


def _summary_response(result: ApplicationWithRisk) -> ApplicationSummaryResponse:
    app = result.application
    return ApplicationSummaryResponse(
        id=app.id,
        reference_no=app.reference_no,
        loan_amount=app.loan_amount,
        status=app.status,
        co_applicant_name=app.co_applicant.full_name if app.co_applicant else None,
        submitted_at=app.submitted_at,
        created_at=app.created_at,
        risk_band=RiskBand(result.risk.band) if result.risk else None,
    )


@router.post(
    "",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a draft application",
)
async def create_application(
    body: CreateApplicationRequest,
    current_user: CurrentUser,
    use_case: Annotated[CreateApplication, Depends(get_create_application)],
) -> ApplicationResponse:
    app = await use_case.execute(
        CreateApplicationCommand(
            applicant_id=current_user.id,
            loan_amount=body.loan_amount,
            loan_purpose=body.loan_purpose,
            co_applicant_full_name=body.co_applicant.full_name,
            co_applicant_relationship=body.co_applicant.relationship,
            co_applicant_email=body.co_applicant.email,
            co_applicant_phone=body.co_applicant.phone,
        )
    )
    return _application_response(app)


@router.get("", response_model=list[ApplicationSummaryResponse], summary="List applications")
async def list_applications(
    current_user: CurrentUser,
    use_case: Annotated[ListApplications, Depends(get_list_applications)],
) -> list[ApplicationSummaryResponse]:
    results = await use_case.execute(current_user.id, current_user.role)
    return [_summary_response(r) for r in results]


@router.get("/{application_id}", response_model=ApplicationResponse, summary="Application detail")
async def get_application(
    application_id: uuid.UUID,
    current_user: CurrentUser,
    use_case: Annotated[GetApplication, Depends(get_get_application)],
) -> ApplicationResponse:
    result = await use_case.execute(application_id, current_user.id, current_user.role)
    return _detail_response(result)


@router.post(
    "/{application_id}/uploads/init",
    response_model=InitUploadResponse,
    summary="Begin an artifact upload (presigned URL)",
)
async def init_upload(
    application_id: uuid.UUID,
    body: InitUploadRequest,
    current_user: CurrentUser,
    use_case: Annotated[InitArtifactUpload, Depends(get_init_upload)],
) -> InitUploadResponse:
    ticket = await use_case.execute(
        InitUploadCommand(
            application_id=application_id,
            kind=body.kind.value,
            content_type=body.content_type,
            filename=body.filename,
        ),
        current_user.id,
        current_user.role,
    )
    return InitUploadResponse(
        artifact_id=ticket.artifact_id,
        upload_url=ticket.upload_url,
        storage_key=ticket.storage_key,
        max_size_bytes=ticket.max_size_bytes,
    )


@router.post(
    "/{application_id}/uploads/confirm",
    response_model=ArtifactResponse,
    summary="Confirm an artifact upload landed",
)
async def confirm_upload(
    application_id: uuid.UUID,
    body: ConfirmUploadRequest,
    current_user: CurrentUser,
    use_case: Annotated[ConfirmArtifactUpload, Depends(get_confirm_upload)],
) -> ArtifactResponse:
    artifact = await use_case.execute(
        ConfirmUploadCommand(application_id=application_id, artifact_id=body.artifact_id),
        current_user.id,
        current_user.role,
    )
    return _artifact_response(artifact)


@router.post(
    "/{application_id}/submit",
    response_model=ApplicationResponse,
    summary="Submit for verification",
)
async def submit_application(
    application_id: uuid.UUID,
    current_user: CurrentUser,
    use_case: Annotated[SubmitApplication, Depends(get_submit_application)],
) -> ApplicationResponse:
    app = await use_case.execute(
        application_id, current_user.id, current_user.role
    )
    return _application_response(app)
