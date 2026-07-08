# Phase 12 — Reports & Analytics

**Project:** AI Co-Applicant Verification Platform (`loan-verification-ai`)
**Status:** Complete — verified end-to-end through the real UI against a live Postgres/Redis/moto-S3/Celery stack.
**Depends on:** Phases 1–11.

> Closes the reporting and compliance-analytics feature bullets from Phase 1:
> a per-application record (PDF/JSON/CSV) combining loan details, risk
> assessment, evidence summary, and full decision history; a compliance bulk
> export of every application; and an analytics dashboard (approval rate,
> risk-band distribution, average decision time/confidence).

## `ai-services` — report rendering

- New `report_generator` module, dependency-light and deterministic like the
  rest of `ai-services`: `contracts.py` (frozen dataclasses —
  `ApplicationReportData`, `RiskSummary`, `EvidenceSummary`, `DecisionRecord`,
  `BulkExportRow`), `pdf_renderer.py` (reportlab `SimpleDocTemplate`, real PDF
  bytes), `json_renderer.py`, `csv_renderer.py`.
- Added a **PEP 561 `py.typed` marker** to `ai-services` and removed
  `ai_services.*` from the backend's mypy `ignore_missing_imports` override —
  this was the correct fix (not a suppression) for cross-package type
  checking: mypy now checks every call into `ai-services` against its real
  signatures instead of treating the whole package as `Any`.
- 11 new `ai-services` unit tests (PDF validity/size, all-fields-present vs.
  all-optional-fields-None, JSON round-trip, CSV header/row structure, bulk
  CSV/JSON). `ruff`/`mypy` clean.

## Backend

- **New ports/DTOs**: `ReportRepository`, `AnalyticsRepository`,
  `GenerateReportCommand`/`ReportDto`/`AnalyticsSummary`. Extended
  `ApplicationRepository` with `list_all()` (compliance/bulk export only —
  deliberately not exposed as a general listing endpoint) and
  `ObjectStorage` with `upload_bytes()` (server-side upload for generated
  artifacts, distinct from the client's presigned-PUT flow).
- **Use cases** (`app/application/use_cases/reports/`):
  - `GenerateApplicationReport` — staff-only; pulls the application, current
    risk score, latest verification-stage scalars (via a
    `build_verification_details` helper extracted from Phase 11's
    `GetVerificationDetails` so both share the same evidence-mapping logic),
    and full decision history; renders the requested format; uploads it;
    records a versioned `reports` row; logs `REPORT_GENERATED`; returns a
    presigned download URL.
  - `GenerateBulkExport` — rejects PDF (`ValidationError`; not meaningful for
    a tabular bulk record), pulls every application via `list_all()`, batches
    current risk scores, renders CSV/JSON, stores with `application_id=None`,
    logs `REPORT_GENERATED` with a `row_count`.
  - `GetReportDownloadUrl` — re-issues a presigned URL for a previously
    generated report and logs `REPORT_EXPORTED` (audit-on-read, same pattern
    as Phase 11's artifact views).
  - `GetAnalyticsSummary` — thin passthrough to a real SQL aggregation
    (`SqlAlchemyAnalyticsRepository`: status/risk-band `GROUP BY` counts,
    `AVG(score)`/`AVG(confidence)`, `AVG(extract(epoch from decided_at -
    submitted_at))` for decided applications, approval rate computed only
    when approved+rejected > 0).
- **Endpoints**: `POST /applications/{id}/reports`, `POST /reports/bulk`,
  `GET /reports/{id}/download` (all staff-only via `require_role`), `GET
  /analytics` (staff-only). Mounted from new `reports.py` and `analytics.py`
  routers.

## Frontend

- `features/analytics/`: `AnalyticsDashboard` (KPI tiles — approved,
  rejected, avg. decision time, avg. confidence — plus total/approval-rate,
  by-status badges, risk-band badges), replacing the Phase-5 static
  placeholder on `/analytics`.
- `features/reports/`: `GenerateReportButton` (three-format button row on the
  officer review detail page, mirroring `DecisionPanel`'s layout) and
  `BulkExportButton` (CSV/JSON, on the analytics page) — both open the
  presigned download URL in a new tab on success.
- `OfficerReviewDetail` gained the report card between the risk/decision
  section and the audit trail.

## Verification performed

- **Backend unit tests** (8 new, 52/52 total): all three per-application
  formats, applicant-role denial (404), unknown-application (404), bulk-PDF
  rejection, bulk coverage of every application regardless of status,
  download-URL re-issue with audit logging, unknown-report (404), analytics
  passthrough.
- **Quality gates**: backend `ruff` + `mypy --strict` clean (161 source
  files, `app` + `tests`); migration parity confirmed with no drift (Phase 12
  introduced no schema changes — `reports` table and the `ReportFormat`/
  `REPORT_GENERATED`/`REPORT_EXPORTED` enums already existed from Phase 3).
  Frontend `tsc --noEmit` clean; `next build` green including the updated
  `/analytics` route and the report-generation code paths.
- **Live curl walkthrough** against real Postgres/Redis/moto-S3 with a single
  Celery worker: registered an applicant, uploaded all three artifacts,
  submitted, confirmed the pipeline produced a risk score directly via the
  database; logged in as the seeded officer, recorded an approve decision;
  generated and downloaded all three per-application report formats (PDF —
  valid `%PDF-` bytes; JSON — correct risk/evidence/decision-history fields;
  CSV — correct header and row); confirmed bulk PDF is rejected (422) and
  bulk CSV/JSON cover every application including ones with no risk score
  yet; re-issued a download URL for a previously generated report; confirmed
  `GET /analytics` returns real aggregates matching the database; confirmed
  an applicant gets 403 attempting to generate a report; confirmed
  `audit_logs` contains `report_generated` (×4: 3 per-application formats +
  1 bulk) and `report_exported` (×1) entries.
- **Full headless-Chromium journey**: logged in as the seeded officer,
  loaded `/analytics` and confirmed the dashboard renders real KPI/status/
  risk-band data (screenshot captured), navigated to `/review/{id}` and
  confirmed the new Report card renders, clicked "PDF" and confirmed the
  generated report opened in a new browser tab pointing at a valid presigned
  moto-S3 URL.

## Notes & operational lesson

- The container restarted between the backend-verification and
  frontend-verification portions of this phase, killing the previously
  running moto server, Celery worker, and Next.js server (as documented as a
  recurring risk in Phases 10–11). All three were re-launched from scratch
  for this phase's live verification pass.
- New wrinkle this phase: `NEXT_PUBLIC_API_BASE_URL` is a Next.js **build-time**
  inlined value for client components — starting `next start` with a
  different value than what `next build` saw does not change the
  already-bundled client code. The backend was restarted on port 8000 (the
  schema default baked into the existing production build) rather than
  rebuilding the frontend, to keep the verification pass fast.
- Self-registration cannot create officer/auditor/admin accounts (a Phase 7
  security decision — role is not honored from the register request body).
  Live verification used the seeded demo officer account
  (`officer@verifyco.bank`, from Phase 11's seed migration) for all
  staff-only endpoints.
- Deferred: no UI for browsing previously generated reports (only
  generate-and-download-now is wired up); no chart/graph visualization on
  the analytics dashboard (KPI tiles and count badges only — no time-series
  trend, since `analytics_repository` only computes present-moment
  aggregates, not historical snapshots).
