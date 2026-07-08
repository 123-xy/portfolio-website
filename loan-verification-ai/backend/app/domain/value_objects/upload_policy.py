"""Upload constraints per artifact kind — the single source of truth for what
the client may upload, enforced server-side at upload-init time (never trust the
client to self-limit)."""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.value_objects.enums import ArtifactKind

_MB = 1024 * 1024


@dataclass(frozen=True)
class KindPolicy:
    allowed_mime_types: frozenset[str]
    max_size_bytes: int
    extension: str


UPLOAD_POLICY: dict[ArtifactKind, KindPolicy] = {
    ArtifactKind.APPLICANT_PHOTO: KindPolicy(
        allowed_mime_types=frozenset({"image/jpeg", "image/png"}),
        max_size_bytes=10 * _MB,
        extension=".jpg",
    ),
    ArtifactKind.COAPPLICANT_PHOTO: KindPolicy(
        allowed_mime_types=frozenset({"image/jpeg", "image/png"}),
        max_size_bytes=10 * _MB,
        extension=".jpg",
    ),
    ArtifactKind.VERIFICATION_VIDEO: KindPolicy(
        allowed_mime_types=frozenset({"video/mp4", "video/webm", "video/quicktime"}),
        max_size_bytes=200 * _MB,
        extension=".mp4",
    ),
    ArtifactKind.DOCUMENT: KindPolicy(
        allowed_mime_types=frozenset({"application/pdf", "image/jpeg", "image/png"}),
        max_size_bytes=20 * _MB,
        extension=".bin",
    ),
}

# Artifacts that must be present (uploaded) before an application can be
# submitted for verification. Documents are optional.
REQUIRED_KINDS: frozenset[ArtifactKind] = frozenset(
    {
        ArtifactKind.APPLICANT_PHOTO,
        ArtifactKind.COAPPLICANT_PHOTO,
        ArtifactKind.VERIFICATION_VIDEO,
    }
)
