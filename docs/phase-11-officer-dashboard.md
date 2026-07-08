# Phase 11 — Officer Dashboard

**Project:** AI Co-Applicant Verification Platform (`loan-verification-ai`)
**Status:** Complete — verified end-to-end through the real UI with a live Celery worker.
**Depends on:** Phases 1–10.

> Implements the officer's review workflow: the evidence pack (photos, video,
> transcript, consent/intent/fraud findings, risk breakdown), the
> approve/reject/request-more-info decision with a mandatory reason, and the
> read side of the audit trail — closing the loop from Phase 1's Officer
> Dashboard and Audit Trail feature bullets.

## Backend

- **New ports/DTOs**: `OfficerRepository` (user → officer profile),
  `OfficerDecisionRepository`, `AuditLogRepository`,
  `VerificationDetails`/`RecordDecisionCommand`/`AuditEntryDto`.
- **Use cases** (`app/application/use_cases/officer_review/`):
  - `GetVerificationDetails` — flattens the pipeline's latest per-stage
    scalars (face match, transcript, consent, intent, fraud) into the
    officer's evidence view. Staff-only (`authorize_staff`, a narrower check
    than the applicant-or-staff `authorize_view`).
  - `GetArtifactDownloadUrl` — issues a short-lived presigned GET URL and
    writes an `ARTIFACT_VIEWED` audit entry on every call — audit-on-read for
    biometric media, per the Phase 1 security requirement, not just
    audit-on-write.
  - `RecordOfficerDecision` — requires a non-empty reason, a valid officer
    profile, and the application actually `pending_review`; writes the
    append-only `officer_decisions` row (linked to the current risk score),
    transitions status (`approve→approved`, `reject→rejected`,
    `request_more_info→more_info_requested`, only the first two mark
    `decided_at`), and writes an `OFFICER_DECISION` audit entry.
  - `GetAuditTrail` — staff-only read of an application's audit history.
- **Endpoints** (`/applications/{id}/verification`, `/artifacts/{artifact_id}/download`,
  `/decision`, `/audit`) mounted from a dedicated `officer.py` router (its own
  OpenAPI tag) but nested under the existing `/applications` resource to reuse
  access-control helpers.
- **Seed migration**: one demo officer account + profile (fixed IDs,
  `officer@verifyco.bank` / `OfficerDemo123!`) since there is no admin
  user-management UI yet and officers are provisioned out-of-band, not
  self-registered (Phase 7 decision). **Loudly marked dev/demo-only in the
  migration itself — must be removed or rotated before production.**

## Frontend

- `ApplicationCard`/`ApplicationList` gained an `hrefBase` prop so the
  officer queue links into `/review/{id}` while the applicant's own list
  still links into `/applications/{id}`.
- `features/officer-review/`: `ArtifactPreview` (on-demand presigned URL →
  `<img>`/`<video>`), `EvidenceCard` (transcript + consent/intent/fraud
  findings), `DecisionPanel`, `AuditTrailCard`, composed in
  `OfficerReviewDetail` at `app/(officer)/review/[id]`.
- **Anti-rubber-stamp gate** (Phase 1 risk #5): the decision buttons stay
  disabled until the officer checks "I have reviewed the photos, video, and
  transcript" *and* enters a reason — a decision cannot be made without that
  explicit acknowledgment.
- Reuses `RiskResultCard` from the applications feature rather than
  duplicating the risk-display logic.

## Verification performed

- **Backend unit tests** (11 new, 42/42 total): verification-details
  flattening, staff-only denial, artifact-download audit logging, 404 on
  unknown artifact, decision approve/request-more-info/empty-reason/
  wrong-status/missing-officer-profile, audit-trail listing and denial.
- **Live Celery worker + Postgres + Redis + moto S3, full curl walkthrough**:
  logged in as the seeded officer, confirmed the queue lists a submitted
  application, fetched verification details (a genuinely varied transcript —
  explicit refusal this run — with matching consent/intent/fraud output),
  fetched a presigned artifact URL, rejected an empty-reason decision (422),
  recorded an approve decision, confirmed the application transitioned to
  `approved` with `decided_at` set (a gap caught and fixed: `decided_at` was
  missing from `ApplicationResponse`), confirmed re-deciding an already-decided
  application is rejected (409), and confirmed the audit trail shows both the
  decision and the artifact view. RBAC re-verified with a second applicant
  account: staff-only endpoints 404, wrong-role decision attempt 403.
- **Full headless-Chromium journey**: registered an applicant, created and
  submitted an application, confirmed the pipeline scored it; logged in as
  the seeded officer in a separate browser context, opened
  `/review/{id}`, confirmed the evidence pack rendered (photos, video
  player, transcript, consent/intent/fraud findings, risk breakdown), checked
  the review-acknowledgment box, entered a reason, and approved — the
  database confirmed the decision was recorded correctly on the very first
  interaction (a client-side confirmation-text assertion had too short a
  timeout and reported a false negative; the underlying API call had already
  succeeded). A follow-up screenshot of the same screen post-decision shows
  the **Approved** badge, the decision panel correctly replaced by "not
  currently awaiting review", and a real **audit trail** listing multiple
  evidence-view entries and the officer decision with real timestamps.
- **Quality gates**: backend `ruff` + `mypy --strict` clean (133 files);
  **42/42 pytest**; migration parity holds; frontend `tsc` clean, `next build`
  green including the new `/review/[id]` route.

## Notes & operational lesson

- Caught **twice** in this build (Phases 10 and 11): stale Celery worker
  and/or Next.js processes surviving from a prior phase's verification run
  will silently serve old code and produce confusing results. Standard
  practice adopted for the rest of this build: enumerate listening
  processes via `/proc/*/net/tcp` before trusting `pgrep`, and kill by PID
  when a pattern-based `pkill` doesn't visibly confirm the target is gone.
- Deferred: an admin UI for provisioning additional officers (the seed
  migration is a stopgap); assigning applications to a specific officer
  (`applications.assigned_officer_id` exists in the schema but queue
  assignment logic is not yet used — all officers currently see the full
  queue); decision reversal/appeal workflow.
