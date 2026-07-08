# Phase 8 — Upload System

**Project:** AI Co-Applicant Verification Platform (`loan-verification-ai`)
**Status:** Complete — verified end-to-end through the real UI against live Postgres + S3-compatible storage.
**Depends on:** Phases 1–7.

> Implements the applications domain (create application + co-applicant), the
> S3-compatible object-storage abstraction, and the presigned direct-to-storage
> upload flow (init → PUT-to-storage → confirm), plus submission gating on
> required artifacts. This is the on-ramp the AI pipeline (Phase 9) hooks onto.

## Backend

**Storage (ports → infra):**
- `ObjectStorage` port with `ensure_bucket` / `create_upload_url` /
  `create_download_url` / `stat` / `delete`.
- `S3ObjectStorage` (boto3, SigV4, path-style) — one `endpoint_url` switch
  serves AWS S3 (prod) and MinIO (dev). Blocking calls run in a thread; the
  bucket is created and given a browser-upload CORS policy at startup.

**Domain & policy:**
- `Application` / `CoApplicant` / `Artifact` entities.
- `upload_policy.py` — allowed MIME types and size caps per kind, and the
  `REQUIRED_KINDS` set for submission — enforced **server-side** (the client is
  never trusted to self-limit).

**Repositories & reference numbers:**
- `ApplicationRepository` / `ArtifactRepository` mapping ORM ⇄ domain entities.
- Human-facing reference numbers (`APP-<year>-<seq>`) from a dedicated
  PostgreSQL sequence (concurrency-safe) — added via a hand-written migration.

**Use cases:**
- `CreateApplication`, `ListApplications` (applicant → own; staff → review
  queue), `GetApplication` (view authorization; denied views 404 to avoid
  enumeration).
- `InitArtifactUpload` — validate kind/content-type against policy, supersede a
  prior single-instance artifact, create a pending row, return a presigned PUT
  URL.
- `ConfirmArtifactUpload` — HEAD the object, enforce the size limit (deleting
  oversized uploads), mark uploaded with the storage checksum.
- `SubmitApplication` — require all `REQUIRED_KINDS` present, transition
  draft → submitted (the pipeline enqueue point for Phase 9).

**Endpoints** under `/api/v1/applications`: `POST ""`, `GET ""`,
`GET /{id}`, `POST /{id}/uploads/init`, `POST /{id}/uploads/confirm`,
`POST /{id}/submit`. Ownership/RBAC enforced per endpoint.

## Frontend

- `applications-api.ts` — typed client mapping snake_case ⇄ camelCase via Zod;
  `uploadArtifact` runs init → direct PUT to storage → confirm.
- TanStack Query hooks (`useApplications`, `useApplication`,
  `useCreateApplication`, `useUploadArtifact`, `useSubmitApplication`).
- Real data throughout (fixtures removed): applications list (loading
  skeletons + empty state), dashboard overview (stats computed from the
  applicant's real applications), officer queue, create-application form, and
  the detail/upload hub (per-artifact upload rows + gated submit).

## Verification performed

- **Backend, live PostgreSQL 16 + moto S3 server**: full curl walkthrough —
  create (reference number allocated), init upload, PUT bytes to the presigned
  URL, confirm (size + checksum recorded), submit-too-early → 422, bad
  content-type → 422, cross-applicant access → 404, submit with all artifacts →
  `submitted`. DB inspection confirmed statuses, sizes, and `submitted_at`.
- **Full-stack, headless Chromium**: register → create application → upload all
  three required artifacts **directly to storage from the browser** (bucket CORS
  honored) → submit. DB confirmed `APP-2026-000004` submitted with three
  uploaded artifacts at the exact byte sizes the browser sent.
- **Quality gates**: backend `ruff` + `mypy --strict` clean (98 files);
  `pytest` 24/24 (adds upload use-case tests: policy rejection, size
  enforcement + cleanup, submit gating, view authorization). Frontend `tsc` +
  `next build` green.

## Notes & deferrals

- `moto` (S3 server mode) stands in for object storage in this environment
  because the MinIO binary download is blocked by the network policy;
  production uses real MinIO/S3 through the same abstraction.
- A `cors_origins` config parsing fix (`NoDecode`) lets the setting accept a
  comma-separated env value.
- Deferred: virus/malage scan hook and resumable/multipart video upload
  (hardening); pipeline enqueue on submit (Phase 9); artifact download
  presigned-GET endpoint for the officer view (Phase 11).
