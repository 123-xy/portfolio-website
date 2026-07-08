from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ObjectStat:
    """Metadata for a stored object, from a HEAD request."""

    size_bytes: int
    etag: str


class ObjectStorage(ABC):
    """Port for S3-compatible object storage.

    Media is uploaded *directly* by the client to storage via a presigned URL,
    so large video/photo bytes never transit the API process. The API only
    hands out short-lived URLs and later verifies the object landed.
    """

    @abstractmethod
    async def ensure_bucket(self) -> None:
        """Create the configured bucket if it does not exist (idempotent)."""
        ...

    @abstractmethod
    async def create_upload_url(
        self, key: str, *, content_type: str, expires_seconds: int = 900
    ) -> str:
        """Presigned PUT URL for a direct client upload."""
        ...

    @abstractmethod
    async def create_download_url(self, key: str, *, expires_seconds: int = 300) -> str:
        """Presigned GET URL for a time-limited download."""
        ...

    @abstractmethod
    async def stat(self, key: str) -> ObjectStat | None:
        """HEAD an object; None if it does not exist."""
        ...

    @abstractmethod
    async def download_bytes(self, key: str) -> bytes:
        """Fetch an object's full contents (used by the AI pipeline)."""
        ...

    @abstractmethod
    async def upload_bytes(self, key: str, data: bytes, *, content_type: str) -> None:
        """Server-side upload (e.g. generated reports) — distinct from the
        client's direct presigned-PUT flow used for large media."""
        ...

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete an object (idempotent)."""
        ...
