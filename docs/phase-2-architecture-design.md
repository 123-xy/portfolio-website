# Phase 2 — Architecture Design

**Project:** AI Co-Applicant Verification Platform (`loan-verification-ai`)
**Status:** Draft for approval
**Depends on:** `docs/phase-1-requirements-analysis.md`

> This document defines service boundaries, the clean-architecture layering
> for both backend and frontend, the Celery task graph for the AI pipeline,
> and the storage strategy. No application code is created in this phase —
> Phase 4 (folder structure) and onward implement what is decided here.

---

## 1. System Context

```
                        ┌───────────────────────────┐
                        │        Browser (Officer /  │
                        │     Applicant / Admin)     │
                        └─────────────┬─────────────┘
                                      │ HTTPS
                        ┌─────────────▼─────────────┐
                        │   Next.js 15 Frontend      │
                        │ (SSR + client, App Router) │
                        └─────────────┬─────────────┘
                                      │ REST /api/v1  (JWT)
                        ┌─────────────▼─────────────┐
                        │      FastAPI Backend      │
                        │  (auth, applications,     │
                        │   uploads, officer,       │
                        │   reports, audit)         │
                        └───┬─────────────┬─────────┘
              ┌─────────────┘             └─────────────┐
   ┌──────────▼──────────┐                  ┌────────────▼───────────┐
   │     PostgreSQL       │                  │         Redis          │
   │ (system of record)   │                  │ (Celery broker/cache)  │
   └──────────────────────┘                  └────────────┬───────────┘
                                                            │
                                              ┌─────────────▼─────────────┐
                                              │   Celery Workers          │
                                              │ ┌───────────────────────┐ │
                                              │ │ worker: media/io      │ │
                                              │ │ worker: ai-heavy      │ │
                                              │ │ beat: scheduler       │ │
                                              │ └───────────┬───────────┘ │
                                              └─────────────┼─────────────┘
                                                             │
                                       ┌─────────────────────▼────────────────────┐
                                       │           ai-services                    │
                                       │ face-detect · face-match · asr           │
                                       │ consent/intent (Gemini) · fraud · risk   │
                                       └─────────────────────┬────────────────────┘
                                                             │
                                              ┌───────────────▼───────────────┐
                                              │  S3-compatible Object Storage  │
                                              │   (AWS S3 / MinIO via config)  │
                                              └────────────────────────────────┘
```

Five deployable units, each independently scalable:

| Unit | Responsibility | Scales on |
|---|---|---|
| `frontend` | UI rendering, client-side interactivity | request concurrency |
| `backend` (FastAPI) | REST API, auth, orchestration, DB access, task enqueue | request concurrency |
| `ai-services` | Pure AI/ML inference functions (face, speech, LLM calls, risk scoring) — a library consumed by Celery workers, not its own HTTP service, to avoid a network hop per inference call in the pipeline | CPU/GPU worker count |
| Celery workers (`worker-media`, `worker-ai-heavy`) | Execute pipeline tasks async | queue depth, split so heavy AI inference never blocks fast I/O tasks (notifications, thumbnailing) |
| `celery-beat` | Scheduled jobs (retention enforcement, stuck-job alerts, analytics rollups) | n/a (single instance) |

`ai-services` is a **library**, not a network service, deliberately: the pipeline
already crosses one process boundary (API → Celery worker via Redis); adding a
second network hop (worker → AI microservice) for every stage would add
latency and failure modes for no isolation benefit, since the worker
container already isolates AI dependencies (OpenCV/InsightFace/Whisper)
from the API container. If a future requirement needs independent scaling
of, say, GPU-bound face matching separate from CPU-bound transcription,
splitting `ai-services` into its own service is a contained change because
the Celery tasks already call it through a narrow interface (see §4).

## 2. Backend Clean Architecture (FastAPI)

Dependency rule: **arrows point inward.** Outer layers depend on inner layers;
inner layers know nothing about outer layers. Domain has zero third-party
imports (no SQLAlchemy, no FastAPI, no boto3).

```
backend/
  domain/                     # innermost — pure Python
    entities/                 # Application, CoApplicant, VerificationResult, RiskScore, ...
    value_objects/            # RiskBand, ConsentStatus, Similarity(0..1), Money, ...
    exceptions/                # DomainError, InvalidStateTransition, ...
    services/                  # pure business rules with no I/O, e.g. RiskWeighting

  application/                # use cases — orchestrate domain + ports
    ports/                    # interfaces (ABCs/Protocols) the domain layer needs from outside
      repositories/            # ApplicationRepository, DocumentRepository, AuditLogRepository, ...
      services/                 # ObjectStorageService, FaceMatchService, TranscriptionService,
                                #   ConsentDetector, IntentClassifier, FraudDetector, NotificationService
    use_cases/                 # SubmitApplication, ConfirmUpload, RunVerificationPipeline,
                                #   RecordOfficerDecision, GenerateReport, ...
    dto/                       # request/response data objects independent of Pydantic/HTTP

  infrastructure/              # implements application/ports — the only layer allowed 3rd-party imports
    db/
      models/                  # SQLAlchemy ORM models
      repositories/            # SqlAlchemyApplicationRepository implements ApplicationRepository
      migrations/              # Alembic
    storage/
      s3_storage_service.py    # implements ObjectStorageService (boto3, S3-compatible)
    ai/
      insightface_matcher.py   # implements FaceMatchService
      whisper_transcriber.py   # implements TranscriptionService
      gemini_consent_detector.py # implements ConsentDetector / IntentClassifier
      opencv_frame_extractor.py
    tasks/                     # Celery task definitions — thin adapters that call use_cases
    auth/
      jwt_provider.py, password_hasher.py
    notifications/
      email_notifier.py

  interfaces/                  # outermost — HTTP presentation
    api/
      v1/
        routers/                # auth.py, applications.py, uploads.py, officer.py, reports.py, audit.py
        schemas/                # Pydantic request/response models
        deps/                   # FastAPI Depends() providers — the composition root wiring ports→infra
    middleware/                 # request-id, error handling, logging, auth

  core/
    config.py                  # pydantic-settings, per-environment
    container.py                # DI container: binds each port to a concrete infra implementation
    logging.py
```

**Why this shape, not a typical Django-style `models.py`/`views.py` split:**
the AI pipeline has multiple interchangeable implementations across the
project's life (InsightFace today, maybe a hosted face API tomorrow;
Whisper today, maybe a hosted ASR API tomorrow). Because `application/`
only depends on the *port* interfaces, swapping `infrastructure/ai/*`
never touches a use case, a router, or a test that mocks the port.

**Dependency Injection**: FastAPI's `Depends()` is the wiring mechanism.
`core/container.py` is the single composition root — it is the only file
that imports both a port and its concrete implementation and binds them.
Routers depend on use cases; use cases depend on port interfaces (typed as
Python `Protocol`s or ABCs); tests inject fakes/mocks for those same ports.
This is Repository Pattern (for persistence) generalized to every external
dependency (storage, AI, notifications).

**Async**: all I/O-bound endpoints (`async def`) — DB access via SQLAlchemy's
async engine (`asyncpg`), storage calls via `aioboto3` or via
`run_in_executor` if a sync SDK is required. AI inference itself
(InsightFace/Whisper) is CPU/GPU-bound and runs in Celery workers, not in the
request/response cycle — the API only enqueues work and reads results.

## 3. Frontend Architecture (Next.js 15 / React 19)

Feature-based, mirroring the same inward-dependency principle adapted to a
frontend:

```
frontend/
  app/                          # Next.js App Router — routes only, no business logic
    (auth)/login/, register/
    (applicant)/dashboard/, applications/[id]/
    (officer)/queue/, applications/[id]/review/
    (admin)/users/, settings/
    layout.tsx, providers.tsx

  features/
    applications/
      domain/                    # zod schemas + inferred TS types (shared shape of API contracts)
      api/                       # typed fetch/query functions (TanStack Query hooks)
      components/                # feature-specific UI (ApplicationCard, StatusBadge, ...)
      hooks/                     # feature-specific hooks (useApplicationStatus, ...)
    verification/                # video/photo upload UI, progress, presigned-upload flow
    officer-review/              # risk score breakdown, decision panel
    audit/
    reports/
    auth/

  shared/
    ui/                          # shadcn/ui primitives + design-system wrappers
    lib/                         # api client (fetch wrapper with auth refresh), utils
    hooks/                       # generic hooks (useDebounce, useMediaUpload, ...)
    types/                       # cross-feature shared types

  middleware.ts                  # route protection by role (redirect unauthenticated/unauthorized)
```

- **Zod** schemas in `features/*/domain` are the single source of truth for a
  shape; both React Hook Form validation and the API client's response
  parsing use the same schema, so a backend contract change fails fast at
  the parse boundary instead of silently rendering `undefined`.
- **Server Components** for read-heavy, non-interactive views (queue lists,
  reports); **Client Components** scoped narrowly to interactive pieces
  (upload widgets, forms, charts) — avoids shipping the whole dashboard as
  client JS.
- State: server state via TanStack Query (cache, refetch, optimistic
  updates for officer decisions); local/UI state via React state; no global
  client store needed at this scope.

## 4. AI Pipeline — Celery Task Graph

### 4.1 Design principles
- **Idempotent, stage-keyed tasks**: every task is keyed by
  `(application_id, stage)` and upserts its `VerificationResults` row —
  re-running a stage (manual retry, or automatic retry after failure)
  never creates duplicate audit rows, it creates a new *version* of that
  stage's result with a monotonic `attempt` number, so audit history is
  additive, never destructive.
- **Two queues, split by cost profile**:
  - `queue=media` — I/O-bound, cheap, fast (upload confirmation, frame
    extraction, audio extraction, notifications, PDF report generation).
  - `queue=ai_heavy` — CPU/GPU-bound inference (face embedding/matching,
    Whisper transcription, Gemini calls, fraud heuristics). Sized and
    scaled independently so a burst of report-generation never starves
    face-matching, and vice versa.
- **Correlation ID propagation**: the API-generated `request_id` for an
  upload is passed into Celery task headers and re-emitted in every log
  line the pipeline produces, so one application's entire pipeline run
  is `grep`-able end to end across worker instances.
- **Failure handling**: per-task `autoretry_for`/`retry_backoff` (e.g. 3
  retries, exponential backoff, capped) for transient errors (network,
  rate limit on Gemini). On final failure, `link_error` routes to a
  `mark_stage_failed` task that writes a terminal `VerificationResults`
  row with `status=failed` and reason, and flags the application
  `needs_attention` — it does **not** silently disappear from the queue.

### 4.2 Task graph

```
confirm_upload(application_id)                         [queue: media]
      │
      ▼
ingest_and_validate(application_id)                      [queue: media]
 (checksum, mime/type check, malware-scan hook, mark artifacts "ingested")
      │
      ├────────────────────────────┬─────────────────────────────┐
      ▼                            ▼                             ▼
 extract_frames               extract_audio                 (documents need
 (application_id)              (application_id)               no AI stage —
 [queue: media]                [queue: media]                 pass-through to
      │                            │                           officer view)
      ▼                            ▼
 detect_faces                 transcribe_audio
 (per sampled frame)          (Whisper)
 [queue: ai_heavy]            [queue: ai_heavy]
      │                            │
      ▼                            ├───────────────┐
 generate_embeddings                ▼               ▼
 [queue: ai_heavy]           detect_consent   detect_intent
      │                     (Gemini + rule    (Gemini)
      ▼                      fallback)        [queue: ai_heavy]
 compare_faces               [queue: ai_heavy]
 (co-applicant photo vs.            │               │
  video-frame embeddings)           └───────┬───────┘
 [queue: ai_heavy]                          │
      │                                     │
      ▼                                     │
 run_fraud_checks  ◄─────────────────────────┘
 (frame consistency, duplicate-face-across-
  applications, embedding replay heuristics)
 [queue: ai_heavy]
      │
      ▼  ── chord (waits on: compare_faces, transcribe_audio→consent→intent, fraud_checks) ──
 calculate_risk_score(application_id)                    [queue: ai_heavy]
 (RiskEngine: weighted composite → band + recommendation + reasons)
      │
      ▼
 finalize_verification(application_id)                   [queue: media]
 (write final VerificationResults summary, update Application.status
  → "pending_officer_review", enqueue notify_officer, write AuditLog)
      │
      ▼
 notify_officer(application_id)                          [queue: media]
```

Implemented with Celery's `chain`/`group`/`chord` primitives: the two
branches (face-match branch, speech branch) run as parallel `group`s, fraud
checks depend on both, and a `chord` callback (`calculate_risk_score`) fires
once every upstream task in the chord has completed — this is what lets
face-matching and transcription run concurrently instead of serially,
which matters for the 5-minute pipeline SLA from Phase 1.

### 4.3 Scheduled jobs (`celery-beat`)
- `enforce_retention_policy` — nightly; purges/archives raw media past its
  configured retention window per artifact type once an application has a
  finalized decision.
- `detect_stuck_pipelines` — every few minutes; flags any application whose
  pipeline has been in a non-terminal stage past SLA, for ops alerting.
- `rollup_analytics` — periodic aggregation into a reporting-friendly
  summary table so the analytics dashboard doesn't run expensive aggregate
  queries against live transactional tables.

## 5. Storage Strategy

### 5.1 Abstraction
`ObjectStorageService` port (application layer) with a single infra
implementation, `S3StorageService`, backed by `boto3`/`aioboto3` pointed at
an `endpoint_url` from config — this is what makes "AWS S3 compatible"
literal: **MinIO in development/on-prem, real AWS S3 in production**,
same code path, only config differs. No code branches on environment.

### 5.2 Key layout

```
{bucket}/
  applications/{application_id}/
    applicant/photo.jpg
    co_applicant/photo.jpg
    co_applicant/verification_video.mp4
    documents/{document_id}.pdf
  derived/{application_id}/
    frames/{frame_index}.jpg
    audio/track.wav
    transcript.json
  reports/{application_id}/report_{version}.pdf
```

Raw originals (`applications/...`) and derived artifacts (`derived/...`)
are separated so retention/lifecycle rules can differ — e.g., derived
frames can be purged shortly after risk scoring completes (they are
reproducible from the original video, which itself is retained per
compliance policy), while the transcript may need longer retention for
audit than a raw frame does.

### 5.3 Upload path
Direct-to-storage presigned upload rather than proxying multi-hundred-MB
video through the FastAPI process:
1. Frontend requests a presigned PUT URL from `POST /api/v1/uploads/init`.
2. Frontend uploads directly to storage using that URL, with progress.
3. Frontend calls `POST /api/v1/uploads/confirm` with the object key.
4. Backend verifies the object exists (HEAD request) and enqueues
   `ingest_and_validate`, kicking off the pipeline in §4.2.

This keeps the API stateless and fast regardless of file size, and matches
the "resumable upload for video" requirement from Phase 1 (multipart
presigned upload for large files).

### 5.4 Security & retention
- Server-side encryption at rest (SSE-S3 or SSE-KMS depending on
  deployment); TLS in transit for all presigned URLs (HTTPS-only
  endpoints).
- Every object read (officer viewing a video/photo) is logged to
  `AuditLogs` with actor + timestamp — enforced by never handing out a
  long-lived public URL; officer-facing media is served via short-TTL
  presigned GET URLs minted per view.
- Retention is config-driven per artifact class and enforced both by
  storage lifecycle rules (coarse, e.g. "delete after 7 years") and by the
  `enforce_retention_policy` beat job (fine-grained, e.g. "purge derived
  frames 24h after risk score is finalized"), resolving the retention vs.
  erasure tension flagged as an open question in Phase 1: raw evidence
  tied to a *decision* is retained per regulatory default; derived,
  reproducible artifacts are purged early to minimize sensitive-data
  surface area.

## 6. Cross-Cutting Concerns

- **Auth**: JWT access tokens (short-lived, ~15 min) + refresh tokens
  (rotated on use, stored hashed in a `refresh_tokens` table so a stolen
  refresh token can be revoked server-side). RBAC enforced via a FastAPI
  dependency (`require_role("officer")`) on every protected router, not
  just conditional UI rendering.
- **Validation**: Pydantic schemas at the API boundary; domain-level
  invariants enforced in `domain/` regardless of what called them (defense
  in depth — a use case is never trusted to have been called only from a
  validated HTTP request).
- **Error handling**: domain exceptions (`InvalidStateTransition`, etc.)
  are translated to HTTP status codes by a single centralized exception
  handler — routers never construct `HTTPException` for business-rule
  violations directly, keeping that mapping in one place.
- **Logging**: structured JSON logs, request-id middleware, correlation ID
  threaded into Celery task headers (§4.1).
- **API versioning**: all routers mounted under `/api/v1`; breaking
  changes get `/api/v2` alongside, never an in-place breaking change.
- **Config**: `pydantic-settings`, one `.env.example` per environment
  (dev/test/prod), secrets never committed, container reads env at
  startup only.

## 7. Deployment Topology (preview of Phase 14)

Anticipated `docker-compose` services (finalized in Phase 14, listed here
because it validates the service boundaries above are actually
composable):

`frontend`, `backend`, `worker-media`, `worker-ai-heavy`, `celery-beat`,
`postgres`, `redis`, `minio` (+ `minio-init` for bucket bootstrap),
`flower` (Celery monitoring, dev-only), `nginx` (prod reverse proxy/TLS
termination). Each has its own Dockerfile under `docker/`, isolating
`worker-ai-heavy`'s much larger dependency set (OpenCV/InsightFace/Whisper
model weights) from the lightweight `backend`/`worker-media` images.

---

## Next Step

Architecture is defined. **Phase 3 (Database Design)** will turn the
entities implied above (`Application`, `CoApplicant`, `Document`, `Photo`,
`Video`, `VerificationResult`, `RiskScore`, `AuditLog`, `Report`,
`Officer`, `Notification`, `RefreshToken`) into a normalized PostgreSQL
schema — tables, columns, types, foreign keys, indexes, and constraints —
before any migration is written.

Awaiting approval to proceed to Phase 3.
