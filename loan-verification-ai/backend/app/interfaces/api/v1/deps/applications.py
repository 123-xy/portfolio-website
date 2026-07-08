from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from app.application.ports.repositories.application_repository import ApplicationRepository
from app.application.ports.repositories.artifact_repository import ArtifactRepository
from app.application.ports.repositories.risk_score_repository import RiskScoreRepository
from app.application.ports.services.object_storage import ObjectStorage
from app.application.ports.services.pipeline import PipelineDispatcher
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
from app.core.config import Settings, get_settings
from app.infrastructure.db.repositories.application_repository import (
    SqlAlchemyApplicationRepository,
)
from app.infrastructure.db.repositories.artifact_repository import SqlAlchemyArtifactRepository
from app.infrastructure.db.repositories.risk_score_repository import SqlAlchemyRiskScoreRepository
from app.infrastructure.storage.s3_storage import S3ObjectStorage
from app.infrastructure.tasks.dispatcher import CeleryPipelineDispatcher
from app.interfaces.api.v1.deps.auth import SessionDep

# One S3 client per process (client construction is non-trivial and thread-safe).
_storage_singleton: ObjectStorage | None = None


def get_object_storage(settings: Annotated[Settings, Depends(get_settings)]) -> ObjectStorage:
    global _storage_singleton
    if _storage_singleton is None:
        _storage_singleton = S3ObjectStorage(settings)
    return _storage_singleton


def get_application_repository(session: SessionDep) -> ApplicationRepository:
    return SqlAlchemyApplicationRepository(session)


def get_artifact_repository(session: SessionDep) -> ArtifactRepository:
    return SqlAlchemyArtifactRepository(session)


def get_risk_score_repository(session: SessionDep) -> RiskScoreRepository:
    return SqlAlchemyRiskScoreRepository(session)


AppRepoDep = Annotated[ApplicationRepository, Depends(get_application_repository)]
ArtifactRepoDep = Annotated[ArtifactRepository, Depends(get_artifact_repository)]
RiskScoreRepoDep = Annotated[RiskScoreRepository, Depends(get_risk_score_repository)]
StorageDep = Annotated[ObjectStorage, Depends(get_object_storage)]


def get_create_application(applications: AppRepoDep) -> CreateApplication:
    return CreateApplication(applications)


def get_list_applications(
    applications: AppRepoDep, risk_scores: RiskScoreRepoDep
) -> ListApplications:
    return ListApplications(applications, risk_scores)


def get_get_application(
    applications: AppRepoDep, risk_scores: RiskScoreRepoDep
) -> GetApplication:
    return GetApplication(applications, risk_scores)


def get_pipeline_dispatcher() -> PipelineDispatcher:
    return CeleryPipelineDispatcher()


def get_submit_application(
    applications: AppRepoDep,
    dispatcher: Annotated[PipelineDispatcher, Depends(get_pipeline_dispatcher)],
) -> SubmitApplication:
    return SubmitApplication(applications, dispatcher)


def get_init_upload(
    applications: AppRepoDep, artifacts: ArtifactRepoDep, storage: StorageDep
) -> InitArtifactUpload:
    return InitArtifactUpload(applications, artifacts, storage)


def get_confirm_upload(
    applications: AppRepoDep, artifacts: ArtifactRepoDep, storage: StorageDep
) -> ConfirmArtifactUpload:
    return ConfirmArtifactUpload(applications, artifacts, storage)
