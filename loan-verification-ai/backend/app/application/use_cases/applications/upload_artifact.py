from __future__ import annotations

import uuid

from app.application.dto.applications import (
    ConfirmUploadCommand,
    InitUploadCommand,
    UploadTicket,
)
from app.application.ports.repositories.application_repository import ApplicationRepository
from app.application.ports.repositories.artifact_repository import ArtifactRepository
from app.application.ports.services.object_storage import ObjectStorage
from app.application.use_cases.applications.access import authorize_owner
from app.domain.entities.application import Artifact
from app.domain.exceptions import (
    InvalidStateTransitionError,
    NotFoundError,
    ValidationError,
)
from app.domain.value_objects.enums import ApplicationStatus, ArtifactKind, UserRole
from app.domain.value_objects.upload_policy import UPLOAD_POLICY

# Kinds an applicant may upload to while assembling or amending an application.
_UPLOADABLE_STATUSES = {ApplicationStatus.DRAFT, ApplicationStatus.MORE_INFO_REQUESTED}
_SINGLETON_KINDS = {
    ArtifactKind.APPLICANT_PHOTO,
    ArtifactKind.COAPPLICANT_PHOTO,
    ArtifactKind.VERIFICATION_VIDEO,
}


def _parse_kind(raw: str) -> ArtifactKind:
    try:
        return ArtifactKind(raw)
    except ValueError as exc:
        raise ValidationError(f"Unknown artifact kind '{raw}'.") from exc


class InitArtifactUpload:
    """Validate the requested upload against policy, create a pending artifact
    row, and return a presigned URL the client uses to upload directly to
    storage. No file bytes pass through the API."""

    def __init__(
        self,
        applications: ApplicationRepository,
        artifacts: ArtifactRepository,
        storage: ObjectStorage,
    ) -> None:
        self._applications = applications
        self._artifacts = artifacts
        self._storage = storage

    async def execute(
        self, command: InitUploadCommand, requester_id: uuid.UUID, role: UserRole
    ) -> UploadTicket:
        app = await self._applications.get_by_id(command.application_id)
        if app is None:
            raise NotFoundError("Application not found.")
        authorize_owner(app, requester_id, role)
        if app.status not in _UPLOADABLE_STATUSES:
            raise InvalidStateTransitionError(
                "Uploads are only allowed while the application is a draft or awaiting more info."
            )

        kind = _parse_kind(command.kind)
        policy = UPLOAD_POLICY[kind]
        if command.content_type not in policy.allowed_mime_types:
            raise ValidationError(
                f"Content type '{command.content_type}' is not allowed for {kind.value}."
            )

        # A re-upload supersedes any prior live artifact of a single-instance kind.
        if kind in _SINGLETON_KINDS:
            await self._artifacts.reject_existing_singletons(app.id, kind)

        artifact_id = uuid.uuid4()
        storage_key = f"applications/{app.id}/{kind.value}/{artifact_id}{policy.extension}"
        co_applicant_id = app.co_applicant.id if app.co_applicant else None
        await self._artifacts.create_pending(
            artifact_id=artifact_id,
            application_id=app.id,
            co_applicant_id=(
                co_applicant_id
                if kind in {ArtifactKind.COAPPLICANT_PHOTO, ArtifactKind.VERIFICATION_VIDEO}
                else None
            ),
            kind=kind,
            storage_key=storage_key,
            mime_type=command.content_type,
            original_filename=command.filename,
        )
        upload_url = await self._storage.create_upload_url(
            storage_key, content_type=command.content_type
        )
        return UploadTicket(
            artifact_id=artifact_id,
            upload_url=upload_url,
            storage_key=storage_key,
            max_size_bytes=policy.max_size_bytes,
        )


class ConfirmArtifactUpload:
    """Confirm a direct upload landed: HEAD the object, enforce the size limit
    (the client cannot be trusted to have honored it), and mark the artifact
    uploaded with its storage checksum."""

    def __init__(
        self,
        applications: ApplicationRepository,
        artifacts: ArtifactRepository,
        storage: ObjectStorage,
    ) -> None:
        self._applications = applications
        self._artifacts = artifacts
        self._storage = storage

    async def execute(
        self, command: ConfirmUploadCommand, requester_id: uuid.UUID, role: UserRole
    ) -> Artifact:
        app = await self._applications.get_by_id(command.application_id)
        if app is None:
            raise NotFoundError("Application not found.")
        authorize_owner(app, requester_id, role)

        artifact = await self._artifacts.get_by_id(command.artifact_id)
        if artifact is None or artifact.application_id != app.id:
            raise NotFoundError("Artifact not found.")

        stat = await self._storage.stat(artifact.storage_key)
        if stat is None:
            raise ValidationError("Upload was not found in storage. Please retry the upload.")

        policy = UPLOAD_POLICY[ArtifactKind(artifact.kind)]
        if stat.size_bytes > policy.max_size_bytes:
            # Reject oversized content and remove it from storage.
            await self._storage.delete(artifact.storage_key)
            raise ValidationError("Uploaded file exceeds the maximum allowed size.")

        await self._artifacts.mark_uploaded(
            artifact.id, size_bytes=stat.size_bytes, checksum_sha256=stat.etag
        )
        artifact.status = "uploaded"
        artifact.size_bytes = stat.size_bytes
        artifact.checksum_sha256 = stat.etag
        return artifact
