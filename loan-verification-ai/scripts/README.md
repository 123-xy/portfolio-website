# scripts/ — Operational & developer scripts

Repeatable operational tasks kept as version-controlled scripts rather
than tribal knowledge. Planned:

- `bootstrap.sh` — one-command local setup (env files, buckets, deps).
- `seed.py` — seed the initial admin user and active `risk_engine_config`.
- `migrate.sh` — run Alembic migrations.
- `lint.sh` / `format.sh` — run the linters/formatters across services.
- `wait-for.sh` — dependency-readiness gate used by containers/CI.

Scripts must be idempotent and safe to re-run.
