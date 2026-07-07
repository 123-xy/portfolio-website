from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from app.domain.value_objects.enums import UserRole


@dataclass(frozen=True)
class AccessTokenClaims:
    """Decoded, validated claims from an access token."""

    user_id: uuid.UUID
    role: UserRole
    token_id: str


@dataclass(frozen=True)
class RefreshTokenMaterial:
    """A freshly minted refresh token: the raw value returned to the client
    once, and the hash + expiry persisted server-side."""

    raw: str
    token_hash: str
    expires_at: datetime


class TokenService(ABC):
    """Port for issuing/validating auth tokens.

    Access tokens are self-contained JWTs; refresh tokens are opaque random
    strings whose hash is stored for server-side revocation.
    """

    @abstractmethod
    def create_access_token(self, user_id: uuid.UUID, role: UserRole) -> str: ...

    @abstractmethod
    def decode_access_token(self, token: str) -> AccessTokenClaims: ...

    @abstractmethod
    def create_refresh_token(self) -> RefreshTokenMaterial: ...

    @abstractmethod
    def hash_refresh_token(self, raw: str) -> str:
        """Deterministic hash used to look up a presented refresh token."""
        ...
