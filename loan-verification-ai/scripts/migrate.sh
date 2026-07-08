#!/usr/bin/env bash
# Apply database migrations. Thin, idempotent wrapper around Alembic so ops
# don't need to remember the working directory / config location.
#
#   scripts/migrate.sh              # upgrade to head
#   scripts/migrate.sh downgrade -1 # any alembic subcommand passes through
#
# Reads DATABASE_URL from the environment (or backend/.env). In the container
# stack this is the `migrate` service's job — this script is for host/manual
# runs.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ -z "${VIRTUAL_ENV:-}" ] && [ -f "${ROOT}/backend/.venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source "${ROOT}/backend/.venv/bin/activate"
fi

cd "${ROOT}/backend"
if [ "$#" -eq 0 ]; then
  exec alembic upgrade head
fi
exec alembic "$@"
