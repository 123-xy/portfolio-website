from functools import lru_cache
from typing import Annotated, Literal, cast

from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

Environment = Literal["development", "test", "production"]


class Settings(BaseSettings):
    """Application configuration, sourced from environment (and .env in dev).

    Validated once at startup so a missing or malformed setting fails loudly
    here rather than as an obscure error at a call site.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )

    # --- General ---
    environment: Environment = "development"
    debug: bool = False
    app_name: str = "AI Co-Applicant Verification Platform"
    api_v1_prefix: str = "/api/v1"
    # Expose Prometheus metrics at /metrics (scraped in the monitoring stack).
    metrics_enabled: bool = True

    # --- Database ---
    # Async DSN (asyncpg) used by the app; Alembic derives a sync DSN from it.
    database_url: PostgresDsn = Field(
        default=cast(PostgresDsn, "postgresql+asyncpg://verify:verify@localhost:5432/verify"),
    )
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_echo: bool = False

    # --- Redis (Celery broker / cache) ---
    redis_url: RedisDsn = Field(default=cast(RedisDsn, "redis://localhost:6379/0"))

    # --- Auth / JWT ---
    jwt_secret_key: str = Field(default="change-me-in-production", min_length=8)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    # --- Account lockout (brute-force mitigation) ---
    max_failed_login_attempts: int = 5
    account_lockout_minutes: int = 15

    # --- CORS ---
    # NoDecode: keep the raw env string (comma-separated) out of pydantic-settings'
    # JSON decoder so the validator below can split it.
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:3000"]
    )

    # --- Object storage (S3-compatible) ---
    s3_endpoint_url: str | None = None
    # Endpoint used ONLY to sign presigned URLs handed to the browser. Needed
    # when the backend reaches storage by an internal name the browser can't
    # resolve — e.g. `http://minio:9000` inside Docker Compose vs
    # `http://localhost:9000` from the host. Leave unset for AWS S3 or any
    # setup where one endpoint serves both (the moto/local dev default).
    s3_public_endpoint_url: str | None = None
    s3_region: str = "us-east-1"
    s3_bucket: str = "verify-artifacts"
    s3_access_key: str | None = None
    s3_secret_key: str | None = None

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors(cls, value: object) -> object:
        # Allow a comma-separated string in env, e.g. "http://a,http://b".
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def sync_database_url(self) -> str:
        """Synchronous DSN (psycopg2) for Alembic migrations."""
        return str(self.database_url).replace("+asyncpg", "")

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor — one instance per process."""
    return Settings()
