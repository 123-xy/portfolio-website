# Deployment Runbook

How to deploy the AI Co-Applicant Verification Platform to a single Docker
host. The stack is `docker compose` with a production overlay (nginx TLS
termination + hardening) and an optional monitoring overlay.

For anything beyond a single host (multi-node, autoscaling), the images and
Compose files map cleanly onto Kubernetes/Helm — that translation is out of
scope here and noted at the end.

## Prerequisites

- A host with Docker Engine + Compose v2, ports 80/443 reachable.
- A DNS record pointing your domain at the host (e.g. `app.example.com`).
- TLS certificates (Let's Encrypt recommended).

## 1. Configure

```bash
cd loan-verification-ai
cp infrastructure/.env.production.example .env
scripts/gen-secrets.sh >> .env      # then edit .env: set domains, S3, TLS paths
```

Fill in every required secret (`JWT_SECRET_KEY`, `POSTGRES_PASSWORD`,
`MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`) and the public URLs
(`CORS_ORIGINS`, `NEXT_PUBLIC_API_BASE_URL`, `S3_PUBLIC_ENDPOINT_URL`). The
prod overlay refuses to start if a required secret is missing.

## 2. TLS certificates

Point `TLS_CERTS_DIR` at a directory containing `fullchain.pem` and
`privkey.pem`. With Let's Encrypt/certbot the live directory works directly:

```bash
# One-time issuance (webroot mode; nginx serves the ACME challenge on :80).
TLS_CERTS_DIR=/etc/letsencrypt/live/app.example.com
```

For local HTTPS testing without a CA, generate a self-signed pair:

```bash
mkdir -p docker/nginx/certs
openssl req -x509 -newkey rsa:2048 -nodes -days 365 \
  -keyout docker/nginx/certs/privkey.pem \
  -out docker/nginx/certs/fullchain.pem \
  -subj "/CN=localhost"
```

## 3. Launch

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

Startup order is enforced by health checks and `depends_on` conditions:
Postgres/Redis become healthy → `migrate` applies `alembic upgrade head` (and
seeds the demo officer) → `backend`/`worker` start → `frontend` starts →
`nginx` starts once backend and frontend are healthy. Only nginx is exposed to
the host (80/443); the app and API are reachable only through it.

Verify:

```bash
docker compose ps                                  # all healthy
curl -fsS https://app.example.com/api/v1/health    # {"status":"ok",...}
curl -fsS https://app.example.com/api/v1/ready      # DB + Redis reachable
```

## 4. Operations

```bash
# Logs
docker compose logs -f backend worker

# Apply new migrations after an update
docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm migrate

# Roll out a new version
git pull && docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# Back up Postgres
docker compose exec postgres pg_dump -U verify verify > backup-$(date +%F).sql
```

## 5. Monitoring (optional)

Add the monitoring overlay to run Prometheus + Grafana alongside the stack:

```bash
docker compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
# Grafana: http://<host>:3001 (admin / $GRAFANA_ADMIN_PASSWORD)
# Prometheus: http://<host>:9090
```

Prometheus scrapes the backend's `/metrics` endpoint (HTTP request rate,
latency, error rate) and evaluates the alert rules in
`monitoring/prometheus/alerts.yml`. The Prometheus datasource is
pre-provisioned in Grafana. In production keep these ports internal (behind
the VPN / not host-published) or add auth at nginx.

## Security checklist

- [ ] All secrets set to generated values; `.env` not committed.
- [ ] TLS certificates valid; HTTP redirects to HTTPS (nginx does this).
- [ ] Postgres/Redis/MinIO are **not** host-published in prod (only nginx is).
- [ ] `ENVIRONMENT=production`, `DEBUG=false` (set by the prod overlay).
- [ ] The Phase-11 seed migration's demo officer
      (`officer@verifyco.bank` / `OfficerDemo123!`) is removed or its password
      rotated before go-live — it is a known dev credential (the migration
      says so in a loud comment).
- [ ] Object-storage bucket is private; media is served only via short-TTL
      presigned URLs (enforced in code).
- [ ] Database backups scheduled.

## Managed / multi-node deployments

The two images (`loan-verification-backend`, `loan-verification-frontend`) and
the Compose service definitions translate directly to Kubernetes: the backend
and worker become two Deployments off the same image with different commands,
`migrate` becomes an init Job, and Postgres/Redis/object storage become managed
services (RDS/ElastiCache/S3) — at which point the bundled `postgres`, `redis`,
and `minio` services are dropped and only the `S3_*`/`DATABASE_URL`/`REDIS_URL`
env change. Authoring those manifests is left for the target platform.
