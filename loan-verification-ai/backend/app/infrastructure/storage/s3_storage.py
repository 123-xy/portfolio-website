from __future__ import annotations

import asyncio
from typing import Any

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from app.application.ports.services.object_storage import ObjectStat, ObjectStorage
from app.core.config import Settings


class S3ObjectStorage(ObjectStorage):
    """S3-compatible storage via boto3. Works against AWS S3 in production and
    MinIO in development through a single `endpoint_url` config switch.

    boto3 is synchronous; blocking calls are offloaded to a thread so they do
    not stall the event loop. Presigned-URL generation is local (no network) but
    is wrapped uniformly for consistency.
    """

    def __init__(self, settings: Settings) -> None:
        self._bucket = settings.s3_bucket
        # Browser direct-uploads are cross-origin (frontend -> storage), so the
        # bucket needs a CORS policy allowing the app origins to PUT/GET.
        self._cors_origins = settings.cors_origins
        # SigV4 + path-style addressing are required for MinIO and safe for S3.
        client_config = Config(signature_version="s3v4", s3={"addressing_style": "path"})
        common = {
            "region_name": settings.s3_region,
            "aws_access_key_id": settings.s3_access_key,
            "aws_secret_access_key": settings.s3_secret_key,
            "config": client_config,
        }
        # Server-side operations (bucket ensure, put/head/get/delete) go through
        # the internal endpoint.
        self._client = boto3.client("s3", endpoint_url=settings.s3_endpoint_url, **common)
        # Presigned URLs are handed to the browser, so they must be signed
        # against the endpoint the browser can actually reach. When a distinct
        # public endpoint is configured, sign with a second client; otherwise
        # one endpoint serves both and we reuse the same client.
        self._signing_client = (
            boto3.client("s3", endpoint_url=settings.s3_public_endpoint_url, **common)
            if settings.s3_public_endpoint_url
            else self._client
        )

    async def ensure_bucket(self) -> None:
        def _ensure() -> None:
            try:
                self._client.head_bucket(Bucket=self._bucket)
            except ClientError:
                self._client.create_bucket(Bucket=self._bucket)
            self._client.put_bucket_cors(
                Bucket=self._bucket,
                CORSConfiguration={
                    "CORSRules": [
                        {
                            "AllowedOrigins": self._cors_origins,
                            "AllowedMethods": ["GET", "PUT"],
                            "AllowedHeaders": ["*"],
                            "ExposeHeaders": ["ETag"],
                            "MaxAgeSeconds": 3600,
                        }
                    ]
                },
            )

        await asyncio.to_thread(_ensure)

    async def create_upload_url(
        self, key: str, *, content_type: str, expires_seconds: int = 900
    ) -> str:
        def _sign() -> str:
            return str(
                self._signing_client.generate_presigned_url(
                    "put_object",
                    Params={"Bucket": self._bucket, "Key": key, "ContentType": content_type},
                    ExpiresIn=expires_seconds,
                )
            )

        return await asyncio.to_thread(_sign)

    async def create_download_url(self, key: str, *, expires_seconds: int = 300) -> str:
        def _sign() -> str:
            return str(
                self._signing_client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self._bucket, "Key": key},
                    ExpiresIn=expires_seconds,
                )
            )

        return await asyncio.to_thread(_sign)

    async def stat(self, key: str) -> ObjectStat | None:
        def _head() -> ObjectStat | None:
            try:
                response: dict[str, Any] = self._client.head_object(Bucket=self._bucket, Key=key)
            except ClientError:
                return None
            return ObjectStat(
                size_bytes=int(response.get("ContentLength", 0)),
                etag=str(response.get("ETag", "")).strip('"'),
            )

        return await asyncio.to_thread(_head)

    async def download_bytes(self, key: str) -> bytes:
        def _get() -> bytes:
            response = self._client.get_object(Bucket=self._bucket, Key=key)
            return bytes(response["Body"].read())

        return await asyncio.to_thread(_get)

    async def upload_bytes(self, key: str, data: bytes, *, content_type: str) -> None:
        await asyncio.to_thread(
            lambda: self._client.put_object(
                Bucket=self._bucket, Key=key, Body=data, ContentType=content_type
            )
        )

    async def delete(self, key: str) -> None:
        await asyncio.to_thread(
            lambda: self._client.delete_object(Bucket=self._bucket, Key=key)
        )
