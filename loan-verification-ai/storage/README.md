# storage/ — Local object-storage mount (development)

Bind-mount target for the MinIO container's data in development, so
uploaded media survives container restarts locally. **Contents are
git-ignored** — this directory holds runtime data, not source.

In production this directory is unused; object storage is real AWS S3 (or
a managed S3-compatible service) configured via `endpoint_url`. The
application code is identical in both cases (single `ObjectStorageService`
abstraction — see `../../docs/phase-2-architecture-design.md` §5).
