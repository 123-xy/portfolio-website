# AI Co-Applicant Verification Platform (`loan-verification-ai`)

Enterprise platform that verifies loan co-applicants using AI-assisted face
matching, speech-to-text, consent/intent detection, fraud checks, and
weighted risk scoring — with a human loan officer as the final
decision-maker and a tamper-evident audit trail throughout.

> **Build status:** scaffolding phase. This repository is being built in
> numbered phases (see `../docs/`). Phase 4 establishes the folder structure
> and module boundaries; implementation code lands in later phases.

## Monorepo layout

| Directory | Purpose |
|---|---|
| `frontend/` | Next.js 15 / React 19 / TypeScript UI (applicant, officer, admin dashboards). Feature-based structure. |
| `backend/` | FastAPI service. Clean architecture: `domain` → `application` → `infrastructure` → `interfaces`. Owns the REST API, auth, orchestration, and DB access. |
| `ai-services/` | Reusable Python AI/ML inference package (face, speech, intent, fraud, risk, reports) consumed by the backend's Celery workers as a library. |
| `docs/` | Architecture, database, API, AI, and deployment documentation (top-level `../docs/` holds the phase design docs). |
| `docker/` | Per-service Dockerfiles and the `docker-compose` definitions for dev and prod. |
| `scripts/` | Operational and developer scripts (bootstrap, seed, lint, migrate). |
| `tests/` | Cross-service end-to-end tests. Unit/integration tests live inside each service. |
| `storage/` | Local object-storage mount (MinIO data) for development. Git-ignored contents. |
| `monitoring/` | Observability configuration (metrics, dashboards, alert rules). |
| `infrastructure/` | Infrastructure-as-code and environment/deployment manifests. |

## Architecture at a glance

Five independently scalable units — `frontend`, `backend` (FastAPI),
`ai-services` (library used by workers), Celery worker pools split into
`media` and `ai_heavy` queues, and `celery-beat` — over PostgreSQL (system
of record), Redis (broker/cache), and S3-compatible object storage (MinIO
in dev, AWS S3 in prod via a single config-driven abstraction).

See the design documents for full detail:
- `../docs/phase-1-requirements-analysis.md`
- `../docs/phase-2-architecture-design.md`
- `../docs/phase-3-database-design.md`

## Getting started

Developer setup, environment configuration, and `docker compose up`
instructions are defined in the DevOps phase (Phase 14) and will be
documented here and in `docs/` at that time.
