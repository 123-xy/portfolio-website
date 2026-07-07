from __future__ import annotations

from app.application.dto.auth import TokenPair
from app.application.ports.repositories.refresh_token_repository import RefreshTokenRepository
from app.application.ports.services.token_service import TokenService
from app.domain.entities.user import User


class TokenIssuer:
    """Issues an access + refresh token pair and persists the refresh token's
    hash. Shared by registration and login so token issuance lives in one place."""

    def __init__(self, token_service: TokenService, refresh_tokens: RefreshTokenRepository) -> None:
        self._tokens = token_service
        self._refresh_tokens = refresh_tokens

    async def issue(
        self, user: User, *, user_agent: str | None, ip_address: str | None
    ) -> TokenPair:
        access = self._tokens.create_access_token(user.id, user.role)
        refresh = self._tokens.create_refresh_token()
        await self._refresh_tokens.create(
            user_id=user.id,
            token_hash=refresh.token_hash,
            expires_at=refresh.expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        return TokenPair(access_token=access, refresh_token=refresh.raw)
