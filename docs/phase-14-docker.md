# Phase 14 — Docker / Containerization

**Project:** AI Co-Applicant Verification Platform (`loan-verification-ai`)
**Status:** Complete (artifacts authored and validated; see the sandbox note on
live `docker compose up`).
**Depends on:** Phases 1–13.

> Packages the whole system — API, Celery worker, frontend, and its backing
> services — into a one-command `docker compose up` stack, so the app runs
> identically on any machine with Docker and Phase 15 (Deployment) has a real
> topology to deploy.

## What was built

```
loan-verification-ai/
  docker-compose.yml          # base stack (8 services)
  docker-compose.dev.yml      # dev overrides: Flower, SQL echo, debug
  .env.docker.example         # documented config template
  .dockerignore               # backend build context (repo root)
  frontend/.dockerignore      # frontend build context
  docker/
    Dockerfile.backend        # multi-stage: build wheels -> slim runtime
    Dockerfile.frontend       # multi-stage: deps -> next build -> standalone
    entrypoint-backend.sh      # defensive TCP wait for DB/Redis
```

### Services (`docker-compose.yml`)

`postgres`, `redis`, `minio` (+ `minio-init` bucket bootstrap), `migrate`
(one-shot `alembic upgrade head`), `backend` (FastAPI/uvicorn), `worker`
(Celery), `frontend` (Next.js). Ordering is enforced with healthchecks +
`depends_on` conditions: the backend and worker only start after Postgres and
Redis report healthy **and** the `migrate` job has completed successfully —
a real migration gate, not a race.

### Backend image (`Dockerfile.backend`)

- Multi-stage: a `builder` stage builds wheels for **both** first-party
  packages (`ai-services` and `backend` — the backend depends on `ai-services`
  by path, so the build context is the `loan-verification-ai/` root, not
  `backend/`) and installs the full dependency closure into an isolated
  `/install` prefix; the `runtime` stage copies only `/install` + the app
  source, so no build toolchain ships in the final image.
- Runs as a non-root user; `curl` included for the Compose healthcheck.
- One image, three commands: API (`uvicorn`, the default), worker (`celery
  … worker`), and migrations (`alembic upgrade head`) — DRY, and guarantees
  all three run identical code.

### Frontend image (`Dockerfile.frontend`)

- Enabled Next.js `output: "standalone"` (in `next.config.mjs`) so the runtime
  image ships only the traced server bundle + static assets, not the full
  `node_modules`.
- `NEXT_PUBLIC_*` values are inlined into the client bundle at **build** time,
  so they're build ARGs (defaulting to the host-published backend URL), not
  runtime env — a subtlety this project already hit during Phase 12
  verification.

### Storage: internal vs. public endpoint (real code change)

In Compose the backend reaches MinIO at `http://minio:9000` (internal network),
but the presigned upload/download URLs it mints are opened by the **browser**,
which can only reach MinIO at `http://localhost:9000` (the host-published
port). A single-endpoint S3 client would sign URLs the browser can't resolve.

Fixed properly in the storage adapter (`s3_storage.py`): added an optional
`S3_PUBLIC_ENDPOINT_URL` setting. When set, presigned URLs are signed by a
second boto3 client pointed at the public endpoint, while all server-side
operations (bucket ensure, put/head/get/delete) use the internal one. When
unset — AWS S3, moto, or any single-host dev setup, i.e. every prior phase —
behavior is byte-for-byte unchanged (the two clients are the same object).
Guarded by new unit tests (`test_s3_storage.py`).

### UTF8, carried into the image

Phase 13 found this sandbox's Postgres had been initialized as `SQL_ASCII`,
which crashes on the `₹` symbol the app emits everywhere. The `postgres`
service pins `POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=C"` so a
compose-provisioned database can never regress into that failure mode. (The
official `postgres` image already defaults to UTF8; this makes it explicit and
guaranteed.)

## Verification performed

Registry blob pulls are blocked by this sandbox's network policy (the same
limitation that blocked the MinIO binary download in Phase 8 — `docker pull`
of any base image returns `Forbidden`), so a live `docker compose up --build`
could not be exercised here. Everything that does **not** require pulling a
base image was validated directly:

- **Compose validity**: `docker compose config` and `docker compose -f
  docker-compose.yml -f docker-compose.dev.yml config` both parse, interpolate
  every `${VAR:-default}`, and resolve the full dependency graph cleanly
  (confirmed the `migrate`/`backend`/`worker` `depends_on` conditions and the
  backend env block resolve as intended).
- **Backend image build approach**: reproduced the `builder` stage's core
  locally — `pip wheel --no-deps` builds clean wheels for both `ai-services`
  and `backend`, and the resulting backend wheel contains the Alembic
  migrations at the path `alembic.ini` expects.
- **Frontend image**: `next build` with `output: "standalone"` produces
  `.next/standalone/server.js`; reproduced the image's runtime layout
  (standalone + copied `.next/static`) and ran `node server.js` exactly as the
  image `CMD` does — it booted and served `/login` with HTTP 200.
- **Entrypoint**: `entrypoint-backend.sh`'s dependency wait was run against the
  live local Postgres and Redis — it detects readiness and execs the command,
  and blocks (rather than starting the app) when a dependency is unreachable.
- **No regressions**: backend `ruff` + `mypy --strict` clean (167 files);
  **73 pytest passed** (69 prior + 4 new storage tests), 90% branch coverage;
  frontend `tsc --noEmit` clean and `next build` green with the standalone
  change.

To run the full stack on any machine with Docker and unrestricted registry
access: `cd loan-verification-ai && docker compose up --build`, then browse
`http://localhost:3000`.

## Notes & deferrals

- **Single worker, not two**: Phase 2 §7 anticipated splitting into
  `worker-media` / `worker-ai-heavy` plus a `celery-beat` scheduler. As
  actually built (Phases 9–12) the pipeline is one Celery task on the
  deterministic default providers, with no beat jobs — so there is one
  `worker` service and one lightweight backend image. `docker/README.md`
  documents this honestly; the split becomes worthwhile only when the real
  model backends (`ai-services`'s `real` extra) are enabled, and the structure
  supports adding it as a second build target + service rather than a rewrite.
- **`nginx` / TLS termination and production hardening** (resource limits,
  secret management, no host-exposed DB/Redis ports, restart/replica policy)
  are deferred to Phase 15 (Deployment), where the target environment is
  chosen — that's where a `docker-compose.prod.yml` overlay or Kubernetes/Helm
  manifests belong.
- **Monitoring** (`monitoring/` — Prometheus/Grafana) remains scaffolding;
  wiring it up is a Phase 15 concern per its README.
