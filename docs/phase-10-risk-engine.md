# Phase 10 — Risk Engine

**Project:** AI Co-Applicant Verification Platform (`loan-verification-ai`)
**Status:** Complete — verified end-to-end through the real UI with a live Celery worker.
**Depends on:** Phases 1–9.

> Implements the weighted risk-scoring engine (Face Match 40% / Speech 20% /
> Intent 20% / Fraud 20%, admin-configurable), adds it as the pipeline's final
> step, persists `risk_scores` with a full explainability trail, and surfaces
> the score/band/recommendation/reasons on both the application list and
> detail screens.

## ai-services: the weighted engine (real logic)

`ai_services/risk_engine/engine.py` — a pure, deterministic function, not a
stand-in:

```
score = 1 − (w_face·face_trust + w_speech·speech_trust + w_intent·intent_trust + w_fraud·fraud_trust)
```

Each `*_trust` component is in `[0, 1]` (higher = more trustworthy); missing
signals fall back to a neutral `0.5` rather than dropping out of the average,
and every component contributes a human-readable reason regardless. Bands and
recommendations reuse the Phase-3 domain enums exactly:
`low → auto_approve_candidate`, `medium → needs_review`,
`high → high_risk_reject_candidate` — preserving the Phase-1 rule that the AI
only ever produces a *candidate* recommendation, never an actual approval.

## Backend

- **DTOs/ports**: `RiskInputs`/`RiskAssessment` (app-layer, mirroring the
  ai-services shapes), `RiskScoringService`, `RiskEngineConfigRepository`,
  `RiskScoreRepository`.
- **Infra**: `AiServicesRiskScoringService` adapter; SQLAlchemy repositories
  for config (reads the single active row) and scores (unsets the prior
  `is_current` row before inserting the new one, honoring the partial unique
  index).
- **Seed migration**: inserts the default active config (version 1, the
  Phase-1 weights, `low_max=0.33`/`medium_max=0.66` thresholds) — idempotent
  via `ON CONFLICT (version) DO NOTHING`.
- **Orchestrator**: `RunVerificationPipeline` now aggregates `latest_scalars()`
  from every stage into `RiskInputs` after the 10 perception/analysis stages,
  scores via the engine, persists both a `risk_scores` row *and* a
  `verification_results` row (`stage=risk_scoring`) for a complete audit
  trail, then moves to `pending_review`. A missing config or scoring failure
  routes to `needs_attention` — same failure-handling shape as every other
  stage.
- **API**: `GET /applications` and `GET /applications/{id}` now return
  `risk_band` / a full `risk` object respectively, via a batched lookup
  (`get_current_batch`) so the list view is a single extra query, not N+1.

## Frontend

- `riskScoreSchema` added to the applications domain schemas; `risk_band` on
  summaries, `risk` on detail.
- `RiskResultCard` — band badge, recommendation, a weighted component
  breakdown (progress bars), and the reasons list, all sourced directly from
  the API.
- `ApplicationCard` shows the risk badge again (list + queue); the detail page
  renders `RiskResultCard` once scoring completes, with a "still processing"
  placeholder before that.

## Verification performed

- **ai-services unit tests** (6): strong signals → low/auto-approve, refusal +
  weak match → high/reject, ambiguous → medium/review, missing signals stay
  bounded and explainable, component scores are bounded and named, custom
  weights/thresholds are respected.
- **Backend orchestrator tests** (extended): a full run persists exactly
  `len(PIPELINE_STAGES) + 1` results ending in a completed `risk_scoring` row
  and a real `RiskAssessment`; a stage failure never reaches risk scoring; a
  missing active config routes to `needs_attention` with a failed
  `risk_scoring` row.
- **Live Celery worker + Postgres + Redis + moto S3**: submitted an
  application through curl; DB inspection showed a coherent low-risk result
  (score 0.0685, band low, `auto_approve_candidate`, reasons citing 0.95 face
  similarity and explicit consent) correctly returned on both list and detail
  endpoints.
- **Full headless-Chromium journey** (after clearing a stale worker process
  left over from Phase 9 — the real bug this phase's E2E pass caught):
  register → create → upload three artifacts → submit → poll until the
  pipeline scores → the detail page renders the `RiskResultCard` with a
  **different, coherent medium-risk result** (score reflecting ambiguous
  consent, misaligned intent, and an elevated fraud signal) — confirming the
  engine responds to real per-application signals, not a fixed value — and
  the applications list shows the matching "Medium risk" badge.
- **Quality gates**: all three packages clean — backend `ruff` + `mypy
  --strict` (117 files) + **31/31 pytest**; ai-services `ruff` + `mypy` +
  **6/6 pytest**; frontend `tsc` clean, `next build` green. Migration parity
  holds (autogenerate reports no drift).

## Notes & deferrals

- Caught and fixed mid-phase: a stale background Celery worker process from
  Phase 9 (running pre-risk-scoring code) was still consuming tasks from the
  shared Redis queue and raced with the newly started worker — a reminder
  that verification infra must be fully torn down between phases, not just
  assumed stopped.
- Deferred: admin UI/endpoint for retuning weights (writes to
  `risk_engine_config`) is an admin feature for a later phase; the DB/config
  layer already supports versioned configs.
- Officer-facing decisioning against this risk score (approve/reject/request
  more info) is Phase 11.
