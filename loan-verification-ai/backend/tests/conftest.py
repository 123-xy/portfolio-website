from __future__ import annotations

import os

# Test-session-wide configuration. `app.core.config.get_settings()` is
# `lru_cache`d — whichever value is in the environment on its first call wins
# for the rest of the process, so these must be set before any test module
# imports `app.*` (module import happens at collection time, before fixtures
# run). Pure unit tests never touch these settings (they exercise use cases
# against in-memory fakes), so setting them unconditionally for the whole
# suite is harmless and keeps behavior independent of collection order.
os.environ.setdefault(
    "DATABASE_URL", "postgresql+asyncpg://verify:verify@127.0.0.1:5433/verify_test"
)
os.environ.setdefault("REDIS_URL", "redis://127.0.0.1:6380/1")
os.environ.setdefault("JWT_SECRET_KEY", "integration-test-secret-key-0123456789")
os.environ.setdefault("S3_ENDPOINT_URL", "http://127.0.0.1:5000")
os.environ.setdefault("S3_BUCKET", "verify-artifacts-test")
os.environ.setdefault("S3_ACCESS_KEY", "test")
os.environ.setdefault("S3_SECRET_KEY", "test")
os.environ.setdefault("S3_REGION", "us-east-1")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:3000")
