# scripts/ — Operational & developer scripts

Repeatable operational tasks kept as version-controlled scripts rather than
tribal knowledge. All are idempotent and safe to re-run.

- `lint.sh` — run every static check CI runs (ruff + mypy across backend and
  ai-services, tsc for the frontend); `--tests` also runs the test suites.
  Mirrors `.github/workflows/ci.yml`, so green locally means green in CI.
- `migrate.sh` — thin Alembic wrapper (`scripts/migrate.sh` upgrades to head;
  any alembic subcommand passes through). For host/manual runs — in the
  container stack the `migrate` service does this.
- `gen-secrets.sh` — generate strong random secrets for a production `.env`
  (prints to stdout; review and store securely, never commit).

Other tasks anticipated in Phase 4's scaffold were absorbed elsewhere:
dependency-readiness waiting lives in `docker/entrypoint-backend.sh`, and
initial data seeding (the demo officer + default risk-engine config) is done by
Alembic migrations rather than a separate `seed.py`.
