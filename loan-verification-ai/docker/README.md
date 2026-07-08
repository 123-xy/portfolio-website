# docker/ — Container definitions

Per-service Dockerfiles kept out of the service directories so the full
deployment topology is visible in one place. The Compose files live at the
`loan-verification-ai/` root (they orchestrate every service, not just the
containers defined here).

## Contents

```
Dockerfile.backend      # FastAPI API + Celery worker (one image, two commands)
Dockerfile.frontend     # Next.js 15 standalone build + runtime
entrypoint-backend.sh   # defensive TCP wait for DB/Redis, then exec the command
README.md
```

Compose files (at the repo root, one level up):

```
../docker-compose.yml       # base stack: postgres, redis, minio, minio-init,
                            #   migrate, backend, worker, frontend
../docker-compose.dev.yml   # dev overrides: Flower (Celery UI), SQL echo, debug
../.env.docker.example      # documented config template (copy to ../.env)
```

## Quick start

```bash
cd ..                       # loan-verification-ai/
docker compose up --build   # http://localhost:3000 (app), :8000/docs (API)
```

Runs the whole system with zero configuration. Copy `.env.docker.example` to
`.env` to override defaults (real secrets, ports, etc.).

## Notes on the topology vs. the Phase 2 preview

Phase 2 §7 anticipated splitting the worker into `worker-media` and
`worker-ai-heavy` (isolating OpenCV/InsightFace/Whisper), plus a `celery-beat`
scheduler. As actually built (Phases 9–12), the verification pipeline is a
**single** Celery task running the deterministic default providers, and there
are no scheduled beat jobs — so there is **one** `worker` service and one
lightweight backend image. The two-worker split and a heavy AI image become
worthwhile only when the real model backends (the `ai-services` `real` extra)
are enabled; the single Dockerfile is structured so that is an additive change
(a second build target + a second worker service), not a rewrite.

`nginx` (TLS termination / reverse proxy) and production hardening overrides
are deferred to Phase 15 (Deployment), where the target environment is chosen.
