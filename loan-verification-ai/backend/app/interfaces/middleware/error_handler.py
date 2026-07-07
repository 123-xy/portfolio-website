import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.domain.exceptions import DomainError
from app.interfaces.middleware.request_id import get_request_id

logger = logging.getLogger("app.errors")


def _error_body(code: str, message: str) -> dict[str, object]:
    body: dict[str, object] = {"error": {"code": code, "message": message}}
    request_id = get_request_id()
    if request_id:
        body["request_id"] = request_id
    return body


def register_exception_handlers(app: FastAPI) -> None:
    """Centralized translation of domain errors and unexpected failures into a
    consistent JSON error envelope. Keeping this in one place means routers and
    use cases never build HTTP error responses themselves."""

    @app.exception_handler(DomainError)
    async def _handle_domain_error(_request: Request, exc: DomainError) -> JSONResponse:
        logger.info("domain_error", extra={"code": exc.code, "detail": exc.message})
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(exc.code, exc.message),
        )

    @app.exception_handler(Exception)
    async def _handle_unexpected(_request: Request, exc: Exception) -> JSONResponse:
        # Never leak internals to the client; the full trace goes to logs only.
        logger.exception("unhandled_exception", extra={"error_type": type(exc).__name__})
        return JSONResponse(
            status_code=500,
            content=_error_body("internal_error", "An unexpected error occurred."),
        )
