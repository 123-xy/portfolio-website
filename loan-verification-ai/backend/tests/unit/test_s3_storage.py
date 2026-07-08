from __future__ import annotations

from urllib.parse import urlparse

import pytest

from app.core.config import Settings
from app.infrastructure.storage.s3_storage import S3ObjectStorage


def _settings(**overrides: object) -> Settings:
    base: dict[str, object] = {
        "s3_endpoint_url": "http://minio:9000",
        "s3_region": "us-east-1",
        "s3_bucket": "verify-artifacts",
        "s3_access_key": "test",
        "s3_secret_key": "test",
    }
    base.update(overrides)
    return Settings(**base)  # type: ignore[arg-type]


def test_single_endpoint_reuses_one_client() -> None:
    """With no public endpoint configured (AWS S3 / moto / single-host dev),
    the signing client is the same object as the server-side client — no
    behavior change from before the split was introduced."""
    storage = S3ObjectStorage(_settings())
    assert storage._signing_client is storage._client


def test_distinct_public_endpoint_builds_a_separate_signing_client() -> None:
    storage = S3ObjectStorage(_settings(s3_public_endpoint_url="http://localhost:9000"))
    assert storage._signing_client is not storage._client


@pytest.mark.parametrize("method", ["create_upload_url", "create_download_url"])
async def test_presigned_urls_use_the_public_endpoint_host(method: str) -> None:
    """The URL handed to the browser must point at the public endpoint
    (localhost), not the internal one (minio) it can't resolve — the core
    reason the split exists for Docker Compose."""
    storage = S3ObjectStorage(_settings(s3_public_endpoint_url="http://localhost:9000"))
    if method == "create_upload_url":
        url = await storage.create_upload_url("reports/x.pdf", content_type="application/pdf")
    else:
        url = await storage.create_download_url("reports/x.pdf")

    host = urlparse(url).hostname
    assert host == "localhost"
    assert "minio" not in url
