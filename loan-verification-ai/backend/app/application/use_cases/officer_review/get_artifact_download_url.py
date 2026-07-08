from __future__ import annotations

import uuid

from app.application.ports.repositories.application_repository import ApplicationRepository
from app.application.ports.repositories.audit_log_repository import AuditLogRepository
from app.application.ports.services.object_storage import ObjectStorage
from app.application.use_cases.applications.access import authorize_view
from app.domain.exceptions import NotFoundError
from app.domain.value_objects.enums import AuditAction, UserRole


class GetArtifactDownloadUrl:
    """Issues a short-lived presigned GET URL for one artifact and records an
    audit-on-read entry — biometric media access must be traceable to a viewer
    and a timestamp (Phase 1 security requirement), not just upload-time."""

    def __init__(
        self,
        applications: ApplicationRepository,
        storage: ObjectStorage,
        audit_log: AuditLogRepository,
    ) -> None:
        self._applications = applications
        self._storage = storage
        self._audit_log = audit_log

    async def execute(
        self,
        application_id: uuid.UUID,
        artifact_id: uuid.UUID,
        requester_id: uuid.UUID,
        role: UserRole,
    ) -> str:
        app = await self._applications.get_by_id(application_id)
        if app is None:
            raise NotFoundError("Application not found.")
        authorize_view(app, requester_id, role)

        artifact = next((a for a in app.artifacts if a.id == artifact_id), None)
        if artifact is None:
            raise NotFoundError("Artifact not found.")

        url = await self._storage.create_download_url(artifact.storage_key)
        await self._audit_log.log(
            action=AuditAction.ARTIFACT_VIEWED,
            actor_user_id=requester_id,
            application_id=application_id,
            target_type="artifact",
            target_id=artifact_id,
            metadata={"kind": artifact.kind},
        )
        return url
