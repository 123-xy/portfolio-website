from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

from app.application.ports.services.token_service import (
    AccessTokenClaims,
    RefreshTokenMaterial,
    TokenService,
)
from app.core.config import Settings
from app.domain.exceptions import AuthenticationError
from app.domain.value_objects.enums import UserRole


class JwtTokenService(TokenService):
    """JWT access tokens (HS256) + opaque, hashed refresh tokens.

    Access tokens are stateless and short-lived. Refresh tokens are random,
    high-entropy strings; only their SHA-256 hash is persisted, so the database
    never holds a usable token.
    """

    def __init__(self, settings: Settings) -> None:
        self._secret = settings.jwt_secret_key
        self._algorithm = settings.jwt_algorithm
        self._access_ttl = timedelta(minutes=settings.access_token_expire_minutes)
        self._refresh_ttl = timedelta(days=settings.refresh_token_expire_days)

    def create_access_token(self, user_id: uuid.UUID, role: UserRole) -> str:
        now = datetime.now(UTC)
        claims = {
            "sub": str(user_id),
            "role": role.value,
            "type": "access",
            "jti": secrets.token_urlsafe(16),
            "iat": int(now.timestamp()),
            "exp": int((now + self._access_ttl).timestamp()),
        }
        return str(jwt.encode(claims, self._secret, algorithm=self._algorithm))

    def decode_access_token(self, token: str) -> AccessTokenClaims:
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
        except JWTError as exc:
            raise AuthenticationError("Invalid or expired access token.") from exc

        if payload.get("type") != "access":
            raise AuthenticationError("Wrong token type.")
        try:
            return AccessTokenClaims(
                user_id=uuid.UUID(payload["sub"]),
                role=UserRole(payload["role"]),
                token_id=str(payload.get("jti", "")),
            )
        except (KeyError, ValueError) as exc:
            raise AuthenticationError("Malformed access token.") from exc

    def create_refresh_token(self) -> RefreshTokenMaterial:
        raw = secrets.token_urlsafe(48)
        return RefreshTokenMaterial(
            raw=raw,
            token_hash=self.hash_refresh_token(raw),
            expires_at=datetime.now(UTC) + self._refresh_ttl,
        )

    def hash_refresh_token(self, raw: str) -> str:
        # SHA-256 is appropriate here: the token is already high-entropy random,
        # so a slow password hash adds nothing, and a fast deterministic hash
        # allows an indexed lookup on presentation.
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()
