#!/usr/bin/env bash
# Backend/worker/migrate entrypoint.
#
# Compose already gates start-up on `depends_on: condition: service_healthy`,
# but this adds a defensive TCP wait so the image is also safe to run outside
# compose (plain `docker run`, Kubernetes without an init container, etc.).
# Set WAIT_FOR_DEPS=0 to skip it.
set -euo pipefail

wait_for_url() {
  # Extract host:port from a DSN like scheme://user:pass@host:port/db and block
  # until the TCP port accepts a connection (or the timeout elapses).
  local dsn="$1" name="$2"
  [ -z "${dsn}" ] && return 0
  python - "$dsn" "$name" <<'PY'
import socket, sys, time
from urllib.parse import urlparse

dsn, name = sys.argv[1], sys.argv[2]
parsed = urlparse(dsn)
host = parsed.hostname
port = parsed.port or (5432 if "postgres" in parsed.scheme else 6379)
if not host:
    sys.exit(0)

deadline = time.time() + 60
while time.time() < deadline:
    try:
        with socket.create_connection((host, port), timeout=2):
            print(f"[entrypoint] {name} reachable at {host}:{port}")
            sys.exit(0)
    except OSError:
        time.sleep(1)
print(f"[entrypoint] timed out waiting for {name} at {host}:{port}", file=sys.stderr)
sys.exit(1)
PY
}

if [ "${WAIT_FOR_DEPS:-1}" = "1" ]; then
  wait_for_url "${DATABASE_URL:-}" "database"
  wait_for_url "${REDIS_URL:-}" "redis"
fi

exec "$@"
