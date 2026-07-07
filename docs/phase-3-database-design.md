# Phase 3 — Database Design

**Project:** AI Co-Applicant Verification Platform (`loan-verification-ai`)
**Status:** Draft for approval
**Depends on:** `docs/phase-1-requirements-analysis.md`, `docs/phase-2-architecture-design.md`

> This document defines the normalized PostgreSQL schema: tables, columns,
> types, foreign keys, indexes, constraints, and enums. It is a design
> document — the actual Alembic migration is written in the backend
> initialization phase (Phase 6). SQL below is illustrative DDL that the
> migration will produce, kept faithful to what will ship.

---

## 1. Conventions

- **Primary keys**: UUID (`uuid` type, default `gen_random_uuid()` via
  `pgcrypto`/`pgcrypto`-provided function or `uuid-ossp`). UUIDs avoid
  leaking volume/ordering information (an incrementing integer PK would
  reveal how many loan applications exist), and let the frontend/API
  generate references without a round-trip.
- **Timestamps**: `timestamptz` (UTC, always). Every table has
  `created_at timestamptz NOT NULL DEFAULT now()`. Mutable tables also
  have `updated_at timestamptz NOT NULL DEFAULT now()` maintained by an
  `updated_at` trigger.
- **Soft delete vs. hard delete**: transactional records (applications,
  decisions) are **never** hard-deleted — they carry a status and an
  archival lifecycle for regulatory retention. `AuditLogs` is strictly
  append-only. Only *derived* storage artifacts (frames) are purged, and
  that happens in object storage, not by deleting DB rows (the DB row
  keeps a tombstone `purged_at`).
- **Money/precision**: loan amounts as `numeric(14,2)` — never floating
  point for currency.
- **Scores/confidence**: `numeric(5,4)` in the range `[0,1]`, enforced by
  `CHECK` constraints. Human-readable percentages are a presentation
  concern, not stored.
- **Enums**: PostgreSQL native `ENUM` types for closed, stable value sets
  (roles, statuses). Enums are extended via migration; this trades a
  little migration friction for DB-level integrity over free-text status
  columns.
- **Naming**: `snake_case`, plural table names, `fk_`/`ix_`/`uq_`/`ck_`
  prefixes on named constraints/indexes.

## 2. Enum Types

```sql
CREATE TYPE user_role       AS ENUM ('admin', 'officer', 'applicant', 'auditor');
CREATE TYPE application_status AS ENUM (
    'draft',              -- created, artifacts not all uploaded
    'submitted',          -- all required artifacts uploaded, queued for pipeline
    'processing',         -- AI pipeline running
    'pending_review',     -- pipeline done, awaiting officer
    'needs_attention',    -- pipeline failed / stuck, ops must look
    'more_info_requested',-- officer asked applicant for more documents
    'approved',
    'rejected'
);
CREATE TYPE artifact_kind   AS ENUM ('applicant_photo','coapplicant_photo','verification_video','document');
CREATE TYPE artifact_status AS ENUM ('pending','uploaded','ingested','validated','rejected','purged');
CREATE TYPE verification_stage AS ENUM (
    'ingest','frame_extraction','face_detection','face_embedding','face_match',
    'audio_extraction','transcription','consent_detection','intent_analysis',
    'fraud_check','risk_scoring'
);
CREATE TYPE stage_status    AS ENUM ('pending','running','completed','failed','skipped');
CREATE TYPE risk_band       AS ENUM ('low','medium','high');
CREATE TYPE recommendation  AS ENUM ('auto_approve_candidate','needs_review','high_risk_reject_candidate');
CREATE TYPE consent_status  AS ENUM ('explicit_yes','ambiguous','explicit_no','not_detected');
CREATE TYPE decision_type   AS ENUM ('approve','reject','request_more_info');
CREATE TYPE report_format    AS ENUM ('pdf','json','csv');
CREATE TYPE notification_channel AS ENUM ('in_app','email');
CREATE TYPE audit_action     AS ENUM (
    'user_login','user_logout','user_login_failed',
    'application_created','artifact_uploaded','artifact_viewed','artifact_purged',
    'pipeline_stage_completed','pipeline_stage_failed',
    'risk_scored','officer_decision','report_generated','report_exported',
    'retention_purge','role_changed'
);
```

## 3. Tables

### 3.1 `users`
Single identity table for all roles (applicants, officers, admins,
auditors). Officer-specific attributes live in a separate `officers`
profile table (§3.3) to keep `users` lean and avoid nullable
officer-only columns on every applicant row.

```sql
CREATE TABLE users (
    id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    email          citext NOT NULL,          -- case-insensitive uniqueness
    password_hash  text   NOT NULL,          -- argon2id
    full_name      text   NOT NULL,
    role           user_role NOT NULL DEFAULT 'applicant',
    is_active      boolean NOT NULL DEFAULT true,
    failed_login_count int NOT NULL DEFAULT 0,
    locked_until   timestamptz,              -- set on lockout, null otherwise
    last_login_at  timestamptz,
    created_at     timestamptz NOT NULL DEFAULT now(),
    updated_at     timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_users_email UNIQUE (email)
);
CREATE INDEX ix_users_role ON users (role);
```

### 3.2 `refresh_tokens`
Refresh tokens stored **hashed** so a DB compromise doesn't yield usable
tokens; rotation-on-use is implemented by marking a token
`revoked_at` and issuing a new row. Enables server-side revocation
(logout-all-devices, stolen-token response).

```sql
CREATE TABLE refresh_tokens (
    id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash   text NOT NULL,              -- sha256 of the opaque token
    issued_at    timestamptz NOT NULL DEFAULT now(),
    expires_at   timestamptz NOT NULL,
    revoked_at   timestamptz,               -- null = active
    replaced_by  uuid REFERENCES refresh_tokens(id), -- rotation chain
    user_agent   text,
    ip_address   inet,
    CONSTRAINT uq_refresh_token_hash UNIQUE (token_hash)
);
CREATE INDEX ix_refresh_tokens_user ON refresh_tokens (user_id) WHERE revoked_at IS NULL;
```

### 3.3 `officers`
Officer profile / assignment metadata, 1:1 with a `users` row of role
`officer`.

```sql
CREATE TABLE officers (
    id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    employee_code text NOT NULL,
    branch_code   text,
    department    text,
    created_at   timestamptz NOT NULL DEFAULT now(),
    updated_at   timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_officers_user UNIQUE (user_id),
    CONSTRAINT uq_officers_employee_code UNIQUE (employee_code)
);
```

### 3.4 `applications`
The aggregate root. `assigned_officer_id` is nullable until the pipeline
finishes and the app enters the review queue.

```sql
CREATE TABLE applications (
    id                 uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    reference_no       text NOT NULL,           -- human-facing, e.g. 'APP-2026-000123'
    applicant_id       uuid NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    assigned_officer_id uuid REFERENCES officers(id) ON DELETE SET NULL,
    loan_amount        numeric(14,2) NOT NULL CHECK (loan_amount > 0),
    loan_purpose       text,
    status             application_status NOT NULL DEFAULT 'draft',
    submitted_at       timestamptz,
    decided_at         timestamptz,
    created_at         timestamptz NOT NULL DEFAULT now(),
    updated_at         timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_applications_reference_no UNIQUE (reference_no)
);
CREATE INDEX ix_applications_status        ON applications (status);
CREATE INDEX ix_applications_applicant     ON applications (applicant_id);
CREATE INDEX ix_applications_officer       ON applications (assigned_officer_id);
-- Officer-queue query is "pending_review ordered by submitted_at": partial index.
CREATE INDEX ix_applications_review_queue  ON applications (submitted_at)
    WHERE status = 'pending_review';
```

### 3.5 `co_applicants`
The person being verified. Per Phase 1's recommended default (no
co-applicant self-login in MVP), this is a data record owned by the
application, not necessarily a `users` row. `linked_user_id` is a nullable
forward-hook for the future "co-applicant logs in and self-records"
upgrade path.

```sql
CREATE TABLE co_applicants (
    id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id uuid NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    linked_user_id uuid REFERENCES users(id) ON DELETE SET NULL, -- future self-login
    full_name      text NOT NULL,
    relationship   text,                      -- 'spouse','guarantor', etc.
    email          citext,
    phone          text,
    created_at     timestamptz NOT NULL DEFAULT now(),
    updated_at     timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_co_applicant_per_application UNIQUE (application_id) -- one co-applicant per app in MVP
);
CREATE INDEX ix_co_applicants_application ON co_applicants (application_id);
```

### 3.6 `artifacts`
Unified table for every uploaded object (photos, video, documents),
discriminated by `kind`. A single table (rather than separate `photos`,
`videos`, `documents` tables) is chosen because every artifact shares the
same lifecycle (upload → ingest → validate → possibly purge), the same
storage-key/checksum/mime columns, and the same audit needs — three
near-identical tables would violate DRY and force `UNION` queries for
"all artifacts on this application." The Phase-1 requirement names
Photos/Videos/Documents as *concepts*; they are modeled as `kind` values,
which is the normalized form.

```sql
CREATE TABLE artifacts (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id  uuid NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    co_applicant_id uuid REFERENCES co_applicants(id) ON DELETE SET NULL, -- set for coapplicant photo/video
    kind            artifact_kind NOT NULL,
    status          artifact_status NOT NULL DEFAULT 'pending',
    storage_key     text NOT NULL,           -- object-storage key (see Phase 2 §5.2)
    original_filename text,
    mime_type       text,
    size_bytes      bigint CHECK (size_bytes >= 0),
    checksum_sha256 text,                     -- integrity + duplicate detection
    uploaded_at     timestamptz,
    validated_at    timestamptz,
    purged_at       timestamptz,             -- tombstone once storage object removed
    rejection_reason text,                    -- set when status='rejected'
    created_at      timestamptz NOT NULL DEFAULT now(),
    updated_at      timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_artifact_storage_key UNIQUE (storage_key)
);
CREATE INDEX ix_artifacts_application ON artifacts (application_id);
CREATE INDEX ix_artifacts_kind        ON artifacts (application_id, kind);
CREATE INDEX ix_artifacts_checksum    ON artifacts (checksum_sha256); -- duplicate-file fraud signal
-- Enforce at most one of each single-instance artifact kind per application
-- (a second verification_video is a re-upload; app logic supersedes the old one).
CREATE UNIQUE INDEX uq_artifacts_singleton_kind ON artifacts (application_id, kind)
    WHERE kind IN ('applicant_photo','coapplicant_photo','verification_video')
      AND status <> 'rejected' AND purged_at IS NULL;
```

### 3.7 `verification_results`
One row per pipeline **stage attempt**. Idempotent, versioned by `attempt`
(Phase 2 §4.1): re-running a stage inserts a new row with a higher
`attempt`, never overwriting history. `payload` is `jsonb` for
stage-specific structured output (e.g. per-frame face boxes, transcript
segments) that would be wasteful to fully normalize and is read as a blob
by the officer UI / risk engine.

```sql
CREATE TABLE verification_results (
    id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id uuid NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    stage          verification_stage NOT NULL,
    attempt        int NOT NULL DEFAULT 1 CHECK (attempt >= 1),
    status         stage_status NOT NULL DEFAULT 'pending',
    -- normalized, queryable per-stage scalar outcomes (null when not applicable):
    similarity_score numeric(5,4) CHECK (similarity_score BETWEEN 0 AND 1),
    confidence       numeric(5,4) CHECK (confidence BETWEEN 0 AND 1),
    consent          consent_status,
    payload          jsonb,                    -- stage-specific detail (frames, transcript, boxes)
    error_reason     text,                     -- set when status='failed'
    started_at       timestamptz,
    completed_at     timestamptz,
    created_at       timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_verification_stage_attempt UNIQUE (application_id, stage, attempt)
);
CREATE INDEX ix_verification_results_app_stage ON verification_results (application_id, stage);
-- "latest attempt per stage" is the hot read; supported by the composite above + app-side max(attempt).
CREATE INDEX ix_verification_results_payload_gin ON verification_results USING gin (payload);
```

### 3.8 `risk_scores`
The composite output of the risk engine. Kept separate from
`verification_results` because it is the *aggregate* decision-support
artifact (one authoritative row per scoring run), and it stores the
weighted breakdown and human-readable reasons that the officer UI renders.
`component_scores` holds the per-factor contributions (face 40 / speech
20 / intent 20 / fraud 20) so the score is fully explainable and
reproducible, and `weights_snapshot` records the weights *as configured
at scoring time* — because weights are admin-configurable, a historical
score must be interpretable against the weights that produced it, not
today's weights.

```sql
CREATE TABLE risk_scores (
    id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id   uuid NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    score            numeric(5,4) NOT NULL CHECK (score BETWEEN 0 AND 1),
    band             risk_band NOT NULL,
    recommendation   recommendation NOT NULL,
    confidence       numeric(5,4) NOT NULL CHECK (confidence BETWEEN 0 AND 1),
    component_scores jsonb NOT NULL,           -- {"face_match":0.9,"speech":0.8,"intent":0.7,"fraud":0.95}
    weights_snapshot jsonb NOT NULL,           -- {"face_match":0.40,"speech":0.20,...}
    reasons          jsonb NOT NULL,           -- ["High face similarity (0.92)","Explicit consent detected",...]
    is_current       boolean NOT NULL DEFAULT true, -- most-recent scoring run for the app
    created_at       timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ix_risk_scores_application ON risk_scores (application_id);
-- exactly one current score per application
CREATE UNIQUE INDEX uq_risk_scores_current ON risk_scores (application_id) WHERE is_current;
CREATE INDEX ix_risk_scores_band ON risk_scores (band);
```

### 3.9 `officer_decisions`
Every approve/reject/request-more-info action, with mandatory reason.
Append-only in spirit — a reversal is a *new* decision row, giving a full
decision history per application rather than a mutated single field.

```sql
CREATE TABLE officer_decisions (
    id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id uuid NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    officer_id     uuid NOT NULL REFERENCES officers(id) ON DELETE RESTRICT,
    decision       decision_type NOT NULL,
    reason         text NOT NULL,             -- required by Phase 1; enforced NOT NULL
    risk_score_id  uuid REFERENCES risk_scores(id), -- the score the officer acted on
    created_at     timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ix_officer_decisions_application ON officer_decisions (application_id, created_at DESC);
CREATE INDEX ix_officer_decisions_officer     ON officer_decisions (officer_id);
```

### 3.10 `reports`
Generated report artifacts (PDF/JSON/CSV), pointing to an object-storage
key. Reports are regenerable but each generation is recorded for audit
(who exported what, when — a compliance concern).

```sql
CREATE TABLE reports (
    id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id uuid REFERENCES applications(id) ON DELETE CASCADE, -- null for bulk/analytics exports
    format         report_format NOT NULL,
    storage_key    text NOT NULL,
    generated_by   uuid NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    version        int NOT NULL DEFAULT 1,
    created_at     timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_report_storage_key UNIQUE (storage_key)
);
CREATE INDEX ix_reports_application ON reports (application_id);
```

### 3.11 `audit_logs`
Strictly append-only, tamper-evident record of every material action
(Phase 1 §3.5, Phase 2 §6). No `updated_at`, no `UPDATE`/`DELETE` in
application code — enforced additionally by a DB rule/trigger and a
restricted DB role in production. `prev_hash`/`entry_hash` form an optional
hash chain so any tampering (row deletion/edit) breaks the chain and is
detectable — this is the "tamper-evident" requirement made concrete.

```sql
CREATE TABLE audit_logs (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    action        audit_action NOT NULL,
    actor_user_id uuid REFERENCES users(id) ON DELETE SET NULL, -- null for system/pipeline actor
    is_system     boolean NOT NULL DEFAULT false,
    application_id uuid REFERENCES applications(id) ON DELETE SET NULL,
    target_type   text,                       -- e.g. 'artifact','risk_score','user'
    target_id     uuid,
    metadata      jsonb,                       -- action-specific context (no PII beyond necessity)
    ip_address    inet,
    user_agent    text,
    prev_hash     text,                        -- entry_hash of the previous row (hash chain)
    entry_hash    text,                        -- hash(prev_hash || canonical(this row))
    created_at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ix_audit_logs_application ON audit_logs (application_id, created_at);
CREATE INDEX ix_audit_logs_actor       ON audit_logs (actor_user_id, created_at);
CREATE INDEX ix_audit_logs_action      ON audit_logs (action, created_at);
CREATE INDEX ix_audit_logs_created     ON audit_logs (created_at);
```

### 3.12 `notifications`
In-app and email notifications (officer: "new application in queue";
applicant: "more documents requested"; ops: "pipeline stuck").

```sql
CREATE TABLE notifications (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    recipient_id  uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    application_id uuid REFERENCES applications(id) ON DELETE CASCADE,
    channel       notification_channel NOT NULL DEFAULT 'in_app',
    title         text NOT NULL,
    body          text NOT NULL,
    is_read       boolean NOT NULL DEFAULT false,
    read_at       timestamptz,
    created_at    timestamptz NOT NULL DEFAULT now()
);
-- Hot query: unread in-app notifications for a user, newest first.
CREATE INDEX ix_notifications_recipient_unread ON notifications (recipient_id, created_at DESC)
    WHERE is_read = false;
```

### 3.13 `risk_engine_config`
Admin-configurable weights/thresholds, versioned. The active row feeds
`weights_snapshot` on each scoring run (§3.8). Storing config in the DB
(rather than only in env) lets an admin retune weights through the UI with
an audit trail, and makes historical scores reproducible.

```sql
CREATE TABLE risk_engine_config (
    id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    version          int NOT NULL,
    weights          jsonb NOT NULL,           -- {"face_match":0.40,"speech":0.20,"intent":0.20,"fraud":0.20}
    thresholds       jsonb NOT NULL,           -- {"low_max":0.33,"medium_max":0.66}
    is_active        boolean NOT NULL DEFAULT false,
    created_by       uuid REFERENCES users(id) ON DELETE SET NULL,
    created_at       timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_risk_engine_config_version UNIQUE (version),
    CONSTRAINT ck_weights_sum CHECK (true) -- weight-sum-to-1 validated in app layer (jsonb sum not trivial in CHECK)
);
CREATE UNIQUE INDEX uq_risk_engine_config_active ON risk_engine_config (is_active) WHERE is_active;
```

## 4. Entity-Relationship Overview

```
users 1───* applications           (applicant_id)
users 1───1 officers               (officers.user_id)
officers 1─* applications          (assigned_officer_id, nullable)
applications 1─1 co_applicants     (one co-applicant per app, MVP)
applications 1─* artifacts
co_applicants 1─* artifacts        (coapplicant photo/video)
applications 1─* verification_results   (one row per stage attempt)
applications 1─* risk_scores       (one is_current)
applications 1─* officer_decisions (append-only history)
applications 1─* reports
applications 1─* notifications
applications 1─* audit_logs        (nullable app_id for non-app events)
users 1───* refresh_tokens
users 1───* notifications          (recipient)
users 1───* audit_logs             (actor, nullable for system)
risk_engine_config (standalone, one active version)
```

Normalization: schema is in **3NF** — no repeating groups, no partial or
transitive dependencies on non-key attributes. The two deliberate
denormalizations are (a) `jsonb` payloads for irregular, stage-specific AI
output (normalizing per-frame face boxes into their own table would add
join cost for data only ever read as a blob), and (b) `is_current` /
`weights_snapshot` on `risk_scores` (a controlled redundancy that makes
historical scores self-contained and reproducible). Both are documented,
intentional trade-offs, not accidents.

## 5. Data Integrity Summary

| Concern | Mechanism |
|---|---|
| Referential integrity | FKs on every relationship; `ON DELETE CASCADE` for owned children (artifacts, results), `RESTRICT` where deletion should be blocked (applicant of an application, officer of a decision), `SET NULL` for optional links (assigned officer). |
| No duplicate identities | `uq_users_email` (citext), `uq_officers_employee_code`. |
| One-of-a-kind artifacts | Partial unique index `uq_artifacts_singleton_kind`. |
| Score/confidence sanity | `CHECK (… BETWEEN 0 AND 1)` on all scores. |
| Exactly one current risk score | Partial unique index `uq_risk_scores_current`. |
| Exactly one active config | Partial unique index `uq_risk_engine_config_active`. |
| Mandatory decision reason | `reason text NOT NULL` on `officer_decisions`. |
| Append-only audit | No `updated_at`; production DB role lacks `UPDATE`/`DELETE` on `audit_logs`; optional hash chain. |
| Idempotent pipeline | `uq_verification_stage_attempt (application_id, stage, attempt)`. |

## 6. Indexing Strategy Rationale

Indexes are added for the **actual hot paths**, not speculatively:
- Officer queue (`applications` partial index on `pending_review`).
- Application-scoped fan-out reads (every child table indexed on
  `application_id`).
- Unread-notification badge (partial index, `is_read = false`).
- Audit search by application / actor / action / time.
- Duplicate-file fraud signal (`artifacts.checksum_sha256`).
- `jsonb` GIN index on `verification_results.payload` only (the one place
  we may need to query inside JSON); other `jsonb` columns are blob-read
  and left unindexed to avoid write amplification.

## 7. Migrations Approach (implemented in Phase 6)

- Alembic, one migration per logical change, autogenerate reviewed by hand
  (never blindly applied).
- Enum creation and extension handled explicitly (Alembic autogenerate is
  weak on enum alterations — these will be hand-written).
- A seed migration/script creates: the initial `admin` user (credentials
  from env, not committed), and the initial active `risk_engine_config`
  (version 1, the 40/20/20/20 weights from Phase 1/2).

---

## Next Step

The schema is defined and normalized. **Phase 4 (Folder Structure)** will
scaffold the `loan-verification-ai/` monorepo layout from Phase 2 §2–3 —
creating the directory tree and placeholder module boundaries for
`frontend/`, `backend/`, `ai-services/`, `docs/`, `docker/`, `scripts/`,
`tests/`, `storage/`, `monitoring/`, `infrastructure/` — before any
implementation code is written.

Awaiting approval to proceed to Phase 4.
