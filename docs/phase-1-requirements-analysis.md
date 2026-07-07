# Phase 1 — Requirements Analysis

**Project:** AI Co-Applicant Verification Platform (`loan-verification-ai`)
**Status:** Draft for approval
**Owner:** Engineering (Staff/Architect)

> This document is the output of Phase 1 of the build workflow. No application
> code is written in this phase. It exists to pin down scope, actors, data,
> compliance constraints, and acceptance criteria so that Phase 2 (architecture)
> and Phase 3 (database design) rest on a settled foundation instead of
> assumptions made mid-build.

---

## 1. Problem Statement

Lenders (banks/NBFCs) require a co-applicant on many loans (joint home loans,
guarantor-backed personal loans, etc.). Today, co-applicant identity and
willing participation is verified manually — a loan officer reviews a photo,
a video call, or a physically-witnessed form. This is slow, inconsistent
across officers, and hard to audit after the fact ("did the co-applicant
actually agree, or did the primary applicant sign on their behalf?").

The platform automates the *evidence gathering and first-pass scoring* of
that verification — face match, spoken consent, and stated intent — while
keeping a **human loan officer as the final decision-maker**. The system
produces a defensible, timestamped audit trail suitable for regulatory
review, not just an application status flag.

## 2. Actors / Roles

| Role | Description | Key permissions |
|---|---|---|
| **Applicant** | Primary loan applicant. Initiates the application, uploads their own documents/photo. | Create application, upload own artifacts, view own status |
| **Co-Applicant** | The person being verified. May or may not have platform login (see §5 open question). | Upload verification video/photo/consent artifacts for their own record |
| **Verification Officer** | Bank/NBFC staff who reviews AI output and makes the approve/reject/more-info decision. | View queue, view all artifacts + AI scores, approve/reject/request-more-docs |
| **Compliance / Auditor** | Read-only role for audit and regulatory review. | View audit trail, export reports; no decision rights |
| **Admin** | Manages users, roles, and system configuration (risk-engine weights, retention policy). | Full RBAC management, configuration |
| **System (AI Pipeline)** | Non-human actor; writes VerificationResults, RiskScores, and AuditLogs entries under a service identity. | Write-only to verification tables via internal service auth |

RBAC is enforced server-side on every endpoint (not just hidden in the UI).

## 3. Functional Scope (MVP)

### 3.1 Authentication & Access
- Register/login with email + password, JWT access token + refresh token rotation.
- Role-based access control: `admin`, `officer`, `applicant`, `auditor`.
- Password policy, account lockout after N failed attempts, audit-logged logins.

### 3.2 Applicant Flow
- Create a loan application; attach a co-applicant record.
- Upload: applicant photo, co-applicant photo, verification video, KYC documents.
- File-type/size validation, virus/malware scan hook, resumable upload for video.
- View application status and history.

### 3.3 AI Verification Pipeline (async, queued)
1. **Ingest** — validate uploaded video/photo/audio; store originals immutably in object storage.
2. **Frame extraction** — sample frames from verification video (FFmpeg).
3. **Face detection** — locate faces per frame (MediaPipe/OpenCV).
4. **Face embedding + matching** — compare co-applicant's live video face against their submitted ID photo (InsightFace); output a similarity score + liveness signal.
5. **Audio extraction** — pull audio track from the video (FFmpeg).
6. **Speech-to-text** — transcribe (Whisper).
7. **Consent detection** — classify whether the transcript contains an explicit, affirmative consent statement (LLM-assisted, Gemini API, with a deterministic keyword/pattern fallback for auditability).
8. **Intent analysis** — classify whether the speaker's stated intent matches the loan context (not coerced, not reading a script under duress signals TBD — see risks).
9. **Fraud/anomaly checks** — deepfake/replay-attack heuristics, duplicate-face-across-applications check, frame-consistency check.
10. **Risk scoring** — weighted composite score (Face Match 40% / Speech confidence 20% / Intent 20% / Fraud signal 20%, configurable) → risk band + recommendation (`auto-approve-candidate`, `needs-review`, `high-risk`).
11. Every stage writes a structured, timestamped result row — pipeline is resumable/replayable per stage for audit and debugging.

### 3.4 Officer Dashboard
- Queue of pending applications (filter/sort by risk band, date, branch).
- Detail view: side-by-side photos, video playback, transcript, risk score breakdown with *reasons*, not just a number.
- Decision actions: approve / reject / request more documents, each requiring a reason (free text, logged).

### 3.5 Audit Trail
- Immutable, append-only log of: every upload, every AI stage result, every officer decision, every document access/download, actor, timestamp, IP/user-agent.
- Auditors can search/filter and export but not alter.

### 3.6 Reports & Analytics
- Per-application PDF report (evidence summary + decision + signatures).
- Bulk export (CSV/JSON) for compliance.
- Analytics dashboard: volume, approval/rejection rates, average risk score trends, average AI confidence, processing SLA (time-to-decision).

## 4. Non-Functional Requirements

| Category | Requirement |
|---|---|
| **Security** | Encryption at rest (DB + object storage) and in transit (TLS). Biometric embeddings and raw media are sensitive personal data — access is role-gated and logged on every read. Secrets via env/secret manager, never committed. |
| **Privacy / Compliance** | Data retention policy per artifact type (configurable, default aligned to local lending regulation — to be confirmed with legal). Right-to-erasure vs. regulatory-retention conflict must be resolved explicitly (see risks). PII minimization in logs. |
| **Auditability** | Every state-changing action must be traceable to an actor and a timestamp; audit log itself must be tamper-evident (append-only, hash-chained or WORM storage recommended). |
| **Availability** | AI pipeline runs async (Celery + Redis) so upload/API latency is decoupled from model inference time. Officer dashboard must not block on pipeline completion. |
| **Scalability** | Stateless API layer, horizontally scalable; media processing workers scale independently from the web tier. |
| **Performance** | API p95 < 300ms for non-AI endpoints. Pipeline SLA target: verification result within 5 minutes of upload for a typical (<3 min) video, tunable. |
| **Observability** | Structured logging, health checks per service, metrics for pipeline stage latency/failure rate, alerting on stuck jobs. |
| **Testability** | Unit tests per service/module, integration tests per API, E2E happy-path + key rejection paths. |
| **Accessibility/UI** | WCAG-AA-minded dashboard, dark/light mode, responsive, loading states — this is a tool bank staff use daily, not a marketing site. |

## 5. Open Questions (need answers before/along Phase 2–3)

1. **Co-applicant login**: does the co-applicant get their own account to self-upload, or does the applicant upload on their behalf? This materially changes the auth model and consent legal validity (self-recorded consent is stronger evidence than third-party-submitted consent).
2. **Regulatory jurisdiction**: which country/regulator (e.g., RBI in India, given NBFC terminology) governs data retention, biometric handling, and consent wording? This affects retention defaults and the consent-detection keyword set.
3. **Liveness/anti-spoofing bar**: is a recorded video sufficient, or is a live/real-time capture (webcam session) required to defend against pre-recorded/deepfake submissions? This significantly affects frontend capture requirements.
4. **Gemini API data handling**: sending transcripts (and potentially frames) to an external LLM API has data-residency implications for a bank/NBFC. Need confirmation this is acceptable, or whether intent/consent detection must run fully on self-hosted models for compliance.
5. **Object storage provider**: "AWS S3 compatible" — confirm whether this is real AWS S3, or a self-hosted equivalent (MinIO) for on-prem/data-residency deployments.
6. **Human-in-the-loop guarantee**: confirm the AI recommendation can *never* auto-approve without an officer action (recommended default: AI never auto-approves, only flags `auto-approve-candidate` for expedited officer review). This is both a UX and a regulatory-liability decision.

Where not answered explicitly, Phase 2 will proceed with the **recommended defaults** stated above (no co-applicant self-login in MVP with a clear upgrade path, no jurisdiction-specific hardcoding beyond configurable retention, no auto-approval without a human, MinIO-compatible storage abstraction so either MinIO or real S3 works via config).

## 6. Out of Scope for MVP (explicitly deferred)

- Mobile native apps (responsive web only).
- Multi-language transcript/consent detection (English-first; architecture allows adding locales later).
- Real-time live video call verification (MVP verifies pre-recorded/uploaded video; live session capture is a fast-follow).
- Multi-tenant white-labeling for multiple lenders in one deployment.

## 7. Success Criteria / Definition of Done for the Platform

- An applicant can create an application and submit all required artifacts end-to-end.
- The AI pipeline runs unattended and produces a risk score with an explainable breakdown for every submission within SLA.
- An officer can review and decide on an application using only the dashboard, with no direct DB/file access needed.
- Every action across the lifecycle is reconstructable from the audit trail alone.
- The system runs fully via `docker compose up` in development, with a documented path to a production deployment.
- CI runs unit + integration tests on every change; no merge without green tests.

## 8. Key Risks

| Risk | Mitigation direction |
|---|---|
| Deepfake / pre-recorded video spoofing the face-match step | Liveness checks (blink/head-turn challenge or randomized on-screen prompt read aloud), frame-consistency heuristics; flagged as a Phase-9 hardening item, not solved by face-match alone. |
| LLM (Gemini) hallucination on consent/intent detection | Consent detection uses a deterministic rule/keyword layer as the system of record; LLM output is advisory and always shown with the officer able to listen/read the transcript directly — never a sole source of truth. |
| Biometric data sensitivity / regulatory exposure | Encrypt at rest, strict RBAC + audit-on-read, configurable retention/erasure, avoid storing raw biometric templates longer than necessary once a decision is finalized (store derived risk outcome; archive/purge raw media per policy). |
| Async pipeline failures leaving applications stuck | Celery retry/backoff with dead-letter queue, stage-level status visible to officer, alerting on stuck jobs past SLA. |
| Officer decision made without reviewing evidence ("rubber-stamping") | UI requires explicit acknowledgment (e.g., video must be played, transcript scrolled) before decision buttons enable — a Phase-11 UX decision, not just a permission. |

---

## Next Step

This document defines scope, actors, and constraints. **Phase 2 (Architecture
Design)** will translate this into: service boundaries, the clean-architecture
layering for both frontend and backend, the async pipeline design (Celery
task graph), and the storage/media strategy — before any folder or code is
created.

Awaiting approval to proceed to Phase 2.
