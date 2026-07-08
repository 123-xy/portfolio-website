# infrastructure/ — Deployment configuration & runbook

Environment provisioning and deployment configuration, kept separate from
application code so infra changes are reviewable and reproducible. Contains no
secrets — only templates and documentation.

- `DEPLOYMENT.md` — the deployment runbook: configure, TLS, launch, operate,
  monitor, and a security checklist for the single-host `docker compose`
  production topology (base stack + `docker-compose.prod.yml` overlay).
- `.env.production.example` — production configuration template (required
  secrets, public URLs, TLS paths). Copy to `../.env` on the host and fill in;
  generate secrets with `scripts/gen-secrets.sh`.

CI/CD lives at the repository root in `.github/workflows/ci.yml` (lint, types,
tests across all services, plus a real Docker image build). Multi-node /
Kubernetes manifests are out of scope for this phase; `DEPLOYMENT.md` describes
how the images and Compose services map onto that target when needed.
