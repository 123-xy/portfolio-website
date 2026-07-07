# infrastructure/ — Infrastructure as Code & deployment manifests

Environment provisioning and deployment configuration kept separate from
application code so infra changes are reviewable and reproducible.

Planned contents (Phase 15):

- Environment manifests (dev / staging / prod) and their `.env.example`
  templates (secrets never committed).
- CI/CD pipeline definitions (build, test, image push, deploy gates).
- Optional IaC (Terraform / Helm / Kubernetes manifests) if the target
  deployment moves beyond `docker-compose`.

Nothing here contains secrets — only templates and structure.
