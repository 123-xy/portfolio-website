#!/usr/bin/env bash
# Run every static check the CI runs, across all services, in one command.
# Mirrors .github/workflows/ci.yml so "green locally" means "green in CI".
#
#   scripts/lint.sh            # lint + typecheck (fast; no tests)
#   scripts/lint.sh --tests    # also run the test suites
#
# Assumes the backend venv is active or lives at backend/.venv, and that
# frontend deps are installed (npm ci).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_TESTS=0
[ "${1:-}" = "--tests" ] && RUN_TESTS=1

# Activate the backend venv if one isn't already active.
if [ -z "${VIRTUAL_ENV:-}" ] && [ -f "${ROOT}/backend/.venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source "${ROOT}/backend/.venv/bin/activate"
fi

echo "==> backend: ruff"
( cd "${ROOT}/backend" && ruff check app tests )
echo "==> backend: mypy"
( cd "${ROOT}/backend" && mypy app tests )

echo "==> ai-services: ruff"
( cd "${ROOT}/ai-services" && ruff check ai_services tests )
echo "==> ai-services: mypy"
( cd "${ROOT}/ai-services" && mypy ai_services )

echo "==> frontend: tsc"
( cd "${ROOT}/frontend" && npm run typecheck )

if [ "${RUN_TESTS}" = "1" ]; then
  echo "==> backend: pytest (unit + integration)"
  ( cd "${ROOT}/backend" && pytest --cov=app --cov-report=term-missing )
  echo "==> ai-services: pytest"
  ( cd "${ROOT}/ai-services" && pytest -q )
fi

echo "==> all checks passed"
