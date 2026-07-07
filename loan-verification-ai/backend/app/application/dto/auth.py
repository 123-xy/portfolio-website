from __future__ import annotations

import uuid
from dataclasses import dataclass

from app.domain.value_objects.enums import UserRole


@dataclass(frozen=True)
class RegisterCommand:
    email: str
    full_name: str
    password: str
    # Self-registration is applicant-only; privileged roles are provisioned by
    # an admin, never chosen by the registrant.
    role: UserRole = UserRole.APPLICANT


@dataclass(frozen=True)
class LoginCommand:
    email: str
    password: str
    user_agent: str | None = None
    ip_address: str | None = None


@dataclass(frozen=True)
class RefreshCommand:
    refresh_token: str
    user_agent: str | None = None
    ip_address: str | None = None


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"  # noqa: S105 (not a secret; the OAuth scheme name)


@dataclass(frozen=True)
class AuthenticatedUser:
    id: uuid.UUID
    email: str
    full_name: str
    role: UserRole
