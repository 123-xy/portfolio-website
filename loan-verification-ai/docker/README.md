# docker/ — Container definitions

Per-service Dockerfiles and Compose files. Kept out of the service
directories so the full deployment topology is visible in one place and so
the heavy AI worker image is clearly separated from the lightweight API
image.

Planned contents (finalized in Phase 14):

```
Dockerfile.backend         # FastAPI + worker-media (lightweight deps)
Dockerfile.worker-ai       # worker-ai-heavy: OpenCV / InsightFace / Whisper + model weights
Dockerfile.frontend        # Next.js build + runtime
docker-compose.yml         # base services
docker-compose.dev.yml     # dev overrides (hot reload, flower, exposed ports)
docker-compose.prod.yml    # prod overrides (nginx TLS, restart policies, no dev tooling)
nginx/                     # reverse-proxy / TLS-termination config (prod)
```

Services: `frontend`, `backend`, `worker-media`, `worker-ai-heavy`,
`celery-beat`, `postgres`, `redis`, `minio` (+ `minio-init`),
`flower` (dev), `nginx` (prod). See
`../../docs/phase-2-architecture-design.md` §7.
