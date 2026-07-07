"""Domain-level exceptions.

These are raised by the domain and application layers and are framework-
agnostic (no HTTP concepts). A single exception handler at the interface layer
maps them to HTTP status codes, so business rules never construct HTTP errors
directly.
"""


class DomainError(Exception):
    """Base class for all domain errors."""

    status_code: int = 400
    code: str = "domain_error"

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code


class NotFoundError(DomainError):
    status_code = 404
    code = "not_found"


class ConflictError(DomainError):
    status_code = 409
    code = "conflict"


class ValidationError(DomainError):
    status_code = 422
    code = "validation_error"


class AuthenticationError(DomainError):
    status_code = 401
    code = "authentication_error"


class AuthorizationError(DomainError):
    status_code = 403
    code = "authorization_error"


class InvalidStateTransitionError(DomainError):
    status_code = 409
    code = "invalid_state_transition"


__all__ = [
    "DomainError",
    "NotFoundError",
    "ConflictError",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "InvalidStateTransitionError",
]
