# Phase 9 — AI Verification Pipeline

**Project:** AI Co-Applicant Verification Platform (`loan-verification-ai`)
**Status:** Complete — verified end-to-end on a live Celery worker against Postgres + Redis + S3-compatible storage.
**Depends on:** Phases 1–8.

> Builds the reusable `ai-services` inference library, the Celery + Redis async
> worker wiring, and the pipeline orchestrator that runs the perception/analysis
> stages on submit and persists an attempt-versioned `verification_results` row
> per stage.

## ai-services library

Dependency-light, pure-Python default providers behind `build_*()` factories;
real backends (OpenCV/MediaPipe/InsightFace/Whisper) implement the same shapes
and are enabled by config, not code changes.

- **Real, auditable logic**: consent detection and intent analysis are genuine
  deterministic rule/keyword classifiers over the transcript — the Phase-1
  "system of record" layer (an LLM can be layered on as advisory later).
- **Real math**: face matching exposes cosine similarity; the default seeds it
  from stable checksums for a realistic, reproducible spread.
- **Stand-ins**: frame/face/audio/transcription front-ends substitute for the
  heavy models, isolated behind the factories.

## Backend

- **Ports**: `StageRunner`, `PipelineDispatcher`, `VerificationResultRepository`;
  `ObjectStorage.download_bytes` and `ArtifactRepository.checksum_seen_on_other_application`
  (a real duplicate-media fraud signal).
- **Orchestrator** (`RunVerificationPipeline`): submitted → processing → run the
  10 stages (ingest → frame extraction → face detect/embed/match → audio →
  transcription → consent → intent → fraud) → pending_review. Each stage is
  attempt-versioned and persisted independently; a stage failure routes the
  application to `needs_attention` instead of dropping it.
- **DeterministicStageRunner** wires `ai-services` + storage to each stage,
  threading intermediate signals (transcript, face similarity) through a shared
  context.
- **Celery**: `celery_app` (Redis broker/backend), `run_verification_pipeline`
  task (fresh async engine per run to avoid cross-event-loop asyncpg issues,
  retry-with-backoff), and `CeleryPipelineDispatcher` (short countdown so the
  submitting transaction commits before the worker reads it). `SubmitApplication`
  now enqueues the pipeline.

## Verification performed

- **Live Celery worker** against Postgres 16 + Redis + moto S3: registered an
  applicant, created an application, uploaded the three artifacts, and
  submitted. The worker picked up the job and the application transitioned
  `submitted → pending_review` within ~4s.
- **Persisted results inspected in the DB**: all 10 stages `completed`
  (attempt 1) with coherent, explainable data — face match `0.72` (detection
  confidence `0.93`), a real consent transcript, **rule-based consent
  `explicit_yes` (0.98) with the exact matched phrases**, intent
  `coapplicant_intent_confirmed` (aligned, with reasons), and fraud score
  `0.19`.
- **Quality gates**: `ruff` + `mypy --strict` clean (108 files); `pytest` 30/30
  — adds the rule-based detector tests (affirmative/refusal/ambiguous/coercion),
  face-matcher determinism, orchestrator success + failure-routing, and a
  full deterministic-stage-runner pass. Migration parity holds.

## Notes & deferrals

- `moto` stands in for S3 (MinIO download blocked by the network policy); real
  model backends and MinIO plug in via the documented seams.
- The `risk_scoring` stage (the final `VerificationStage`) and the `risk_scores`
  row are **Phase 10** — the pipeline currently ends at `pending_review` after
  the perception/analysis stages, which is the risk engine's input surface.
- Deferred: Celery beat `detect_stuck_pipelines` job + Flower monitoring
  (Phase 14), and the officer-facing rendering of these results (Phase 11).
