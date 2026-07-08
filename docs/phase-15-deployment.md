# Phase 15 — Deployment

**Project:** AI Co-Applicant Verification Platform (`loan-verification-ai`)
**Status:** Complete — the final phase.
**Depends on:** Phases 1–14.

> Turns the Phase-14 container stack into something deployable and operable:
> a hardened production overlay with TLS termination, a CI pipeline that gates
> every push, real application metrics with a Prometheus/Grafana stack,
> operational scripts, and a deployment runbook.

## What was built

### Production overlay + reverse proxy

- `docker-compose.prod.yml` — layers onto the base stack:
  - Adds **nginx** (`docker/nginx/`) as the only host-exposed service (80/443).
    It terminates TLS, redirects HTTP→HTTPS, sets security headers (HSTS,
    X-Content-Type-Options, X-Frame-Options, Referrer-Policy), gzips, and
    reverse-proxies `/api/` + `/docs|/redoc|/openapi.json` to the backend and
    everything else to the frontend.
  - **Drops host port publishing** on `backend` and `frontend` (`ports: !reset
    []`) — they're reachable only through nginx.
  - **Requires real secrets**: `JWT_SECRET_KEY`, `POSTGRES_PASSWORD`,
    `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD` use `${VAR:?…}` syntax, so compose
    refuses to start with dev defaults. `ENVIRONMENT=production`, `DEBUG=false`.
    `restart: always` throughout.

### CI/CD

- `.github/workflows/ci.yml` — three jobs on every push/PR:
  - **backend**: spins up Postgres + Redis service containers and a moto S3
    mock, then runs `ruff`, `mypy --strict`, and the full `pytest` suite (unit
    + integration) with the coverage gate — plus the ai-services checks.
  - **frontend**: `npm ci`, `tsc --noEmit`, `next build`.
  - **docker-build**: builds both images for real (buildx) — the live
    `docker build` that the dev sandbox couldn't run (registry pulls are
    blocked there; GitHub's runners can pull).

### Observability (real metrics, not scaffolding)

- Added `prometheus-fastapi-instrumentator` and a small
  `infrastructure/observability/metrics.py`; `create_app()` now exposes
  `/metrics` (guarded by a `metrics_enabled` setting) with per-handler request
  rate, latency histogram, error rate, and in-progress gauge.
- `docker-compose.monitoring.yml` runs Prometheus + Grafana; Prometheus scrapes
  the backend and evaluates `monitoring/prometheus/alerts.yml` (backend down,
  >5% 5xx, high p95 latency); Grafana gets the datasource pre-provisioned.

### Operations

- `scripts/lint.sh` (runs every CI check locally; `--tests` adds the suites),
  `scripts/migrate.sh` (Alembic wrapper), `scripts/gen-secrets.sh` (generate
  production secrets).
- `infrastructure/DEPLOYMENT.md` — full runbook (configure → TLS → launch →
  operate → monitor) with a go-live security checklist.
- `infrastructure/.env.production.example` — production config template.

## Verification performed

Registry blob pulls remain blocked in this sandbox (documented in Phases 8 and
14), so a live `docker compose up` / image build could not run here — that's
exactly what the CI `docker-build` job covers on GitHub's runners. Everything
not requiring a registry pull was validated directly:

- **All four Compose configurations parse, interpolate, and resolve**:
  `docker compose config` passes for the base, `+dev`, `+prod`, and
  `+monitoring` combinations. Confirmed the prod overlay's required-secret
  guard actually fails closed (unsetting `JWT_SECRET_KEY` aborts with a clear
  message) and that `backend`/`frontend` host ports are cleared while nginx
  publishes 80/443.
- **Metrics work end-to-end**: exercised `/metrics` in-process — it returns
  Prometheus-format `http_requests_total` (et al.) with per-handler labels
  after real traffic. Guarded by a new test.
- **CI + Prometheus YAML** parse cleanly; the alert expressions reference the
  exact metric names the instrumentator emits.
- **Scripts run**: `scripts/lint.sh` executes green across all three services;
  `gen-secrets.sh` produces secrets; all scripts pass `bash -n`.
- **No regressions**: backend `ruff` + `mypy --strict` clean (169 files),
  **74 pytest pass** (73 prior + 1 metrics test), 90% branch coverage;
  frontend `tsc` + `next build` green.

## Notes & honest gaps

- **Worker metrics**: the backend exposes HTTP metrics, but the Celery worker
  is a task process with no HTTP surface, so pipeline-stage latency/failure and
  per-queue depth (Phase 2 §4.3) aren't scraped yet — that needs a worker-side
  exporter/pushgateway. Documented in `monitoring/README.md`; the HTTP metrics
  and alerts that *are* wired up are real and functional.
- **Single-host topology**: the deliverables target one Docker host. The
  runbook explains how the two images + Compose services map onto Kubernetes
  (backend/worker as Deployments off one image, `migrate` as an init Job,
  Postgres/Redis/S3 as managed services) but those manifests are left to the
  target platform rather than guessed at.
- **Demo officer credential**: the Phase-11 seed migration's
  `officer@verifyco.bank` / `OfficerDemo123!` is a known dev credential (the
  migration says so loudly); the go-live checklist calls out removing/rotating
  it before production.

## Build complete

This is the last of the 15 phases. The platform is built end-to-end:
requirements → architecture → database → scaffolding → frontend → backend →
auth → uploads → AI pipeline → risk engine → officer dashboard → reports &
analytics → testing → Docker → deployment. Each phase's design and verification
is documented in `docs/phase-*.md`.
