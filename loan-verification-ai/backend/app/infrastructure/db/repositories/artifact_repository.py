from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.repositories.artifact_repository import ArtifactRepository
from app.domain.entities.application import Artifact as ArtifactEntity
from app.domain.value_objects.enums import ArtifactKind, ArtifactStatus
from app.infrastructure.db.models.artifact import Artifact as ArtifactModel


def _to_entity(model: ArtifactModel) -> ArtifactEntity:
    return ArtifactEntity(
        id=model.id,
        application_id=model.application_id,
        kind=model.kind.value,
        status=model.status.value,
        storage_key=model.storage_key,
        original_filename=model.original_filename,
        mime_type=model.mime_type,
        size_bytes=model.size_bytes,
        checksum_sha256=model.checksum_sha256,
    )


class SqlAlchemyArtifactRepository(ArtifactRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_pending(
        self,
        *,
        artifact_id: uuid.UUID,
        application_id: uuid.UUID,
        co_applicant_id: uuid.UUID | None,
        kind: ArtifactKind,
        storage_key: str,
        mime_type: str,
        original_filename: str | None,
    ) -> ArtifactEntity:
        model = ArtifactModel(
            id=artifact_id,
            application_id=application_id,
            co_applicant_id=co_applicant_id,
            kind=kind,
            status=ArtifactStatus.PENDING,
            storage_key=storage_key,
            mime_type=mime_type,
            original_filename=original_filename,
        )
        self._session.add(model)
        await self._session.flush()
        return _to_entity(model)

    async def get_by_id(self, artifact_id: uuid.UUID) -> ArtifactEntity | None:
        model = await self._session.get(ArtifactModel, artifact_id)
        return _to_entity(model) if model else None

    async def mark_uploaded(
        self, artifact_id: uuid.UUID, *, size_bytes: int, checksum_sha256: str | None
    ) -> None:
        await self._session.execute(
            update(ArtifactModel)
            .where(ArtifactModel.id == artifact_id)
            .values(
                status=ArtifactStatus.UPLOADED,
                size_bytes=size_bytes,
                checksum_sha256=checksum_sha256,
                uploaded_at=datetime.now(UTC),
            )
        )

    async def reject_existing_singletons(
        self, application_id: uuid.UUID, kind: ArtifactKind
    ) -> None:
        await self._session.execute(
            update(ArtifactModel)
            .where(
                ArtifactModel.application_id == application_id,
                ArtifactModel.kind == kind,
                ArtifactModel.status != ArtifactStatus.REJECTED,
                ArtifactModel.purged_at.is_(None),
            )
            .values(status=ArtifactStatus.REJECTED, rejection_reason="Superseded by re-upload")
        )
