from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from app.domain.entities.application import Artifact
from app.domain.value_objects.enums import ArtifactKind


class ArtifactRepository(ABC):
    """Persistence port for uploaded artifacts."""

    @abstractmethod
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
    ) -> Artifact: ...

    @abstractmethod
    async def get_by_id(self, artifact_id: uuid.UUID) -> Artifact | None: ...

    @abstractmethod
    async def mark_uploaded(
        self, artifact_id: uuid.UUID, *, size_bytes: int, checksum_sha256: str | None
    ) -> None: ...

    @abstractmethod
    async def reject_existing_singletons(
        self, application_id: uuid.UUID, kind: ArtifactKind
    ) -> None:
        """Reject any prior live artifact of a single-instance kind so a
        re-upload supersedes it (keeps the singleton partial index satisfied)."""
        ...
