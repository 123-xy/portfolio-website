#!/usr/bin/env bash
# Generate strong random secrets for a production `.env`. Prints to stdout —
# review, then paste into your secrets store (never commit the result).
#
#   scripts/gen-secrets.sh
set -euo pipefail

gen() { openssl rand -base64 "${1:-32}" | tr -d '\n'; }

echo "# Generated $(date -u +%Y-%m-%dT%H:%M:%SZ) — store securely, do not commit."
echo "JWT_SECRET_KEY=$(gen 48)"
echo "POSTGRES_PASSWORD=$(gen 24)"
echo "MINIO_ROOT_USER=verify-$(gen 6 | tr -dc 'a-z0-9')"
echo "MINIO_ROOT_PASSWORD=$(gen 24)"
echo "GRAFANA_ADMIN_PASSWORD=$(gen 18)"
