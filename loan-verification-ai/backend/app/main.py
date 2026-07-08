import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.infrastructure.db.session import dispose_engine
from app.interfaces.api.v1.router import api_router
from app.interfaces.middleware.error_handler import register_exception_handlers
from app.interfaces.middleware.request_id import RequestIdMiddleware

logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    configure_logging()
    settings = get_settings()
    logger.info("startup", extra={"environment": settings.environment, "version": __version__})
    # Ensure the object-storage bucket exists (idempotent); failures here are
    # logged but non-fatal so the API still serves non-upload traffic.
    try:
        from app.infrastructure.storage.s3_storage import S3ObjectStorage

        await S3ObjectStorage(settings).ensure_bucket()
    except Exception:
        logger.warning("bucket_ensure_failed", exc_info=True)
    yield
    await dispose_engine()
    logger.info("shutdown")


def create_app() -> FastAPI:
    """Application factory. Building the app here (rather than at import time as
    a module global) keeps it testable and lets config drive construction."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        description=(
            "AI-assisted loan co-applicant verification: face match, spoken "
            "consent, intent analysis, fraud checks, and weighted risk scoring "
            "with human officer review and a tamper-evident audit trail."
        ),
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Order matters: request-id outermost so every log line (including errors)
    # carries the correlation id.
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
