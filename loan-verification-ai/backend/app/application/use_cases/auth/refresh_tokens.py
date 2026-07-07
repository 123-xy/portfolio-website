from __future__ import annotations

from datetime import UTC, datetime

from app.application.dto.auth import RefreshCommand, TokenPair
from app.application.ports.repositories.refresh_token_repository import RefreshTokenRepository
from app.application.ports.repositories.user_repository import UserRepository
from app.application.ports.services.token_service import TokenService
from app.application.use_cases.auth.token_issuer import TokenIssuer
from app.domain.exceptions import AuthenticationError


class RefreshAccessToken:
    """Rotate a refresh token: validate the presented token, revoke it, and
    issue a brand-new pair. Rotation means a stolen-and-used refresh token is
    invalidated on the next legitimate refresh, and the old token can never be
    replayed."""

    def __init__(
        self,
        users: UserRepository,
        refresh_tokens: RefreshTokenRepository,
        token_service: TokenService,
        token_issuer: TokenIssuer,
    ) -> None:
        self._users = users
        self._refresh_tokens = refresh_tokens
        self._token_service = token_service
        self._token_issuer = token_issuer

    async def execute(self, command: RefreshCommand) -> TokenPair:
        now = datetime.now(UTC)
        token_hash = self._token_service.hash_refresh_token(command.refresh_token)
        stored = await self._refresh_tokens.get_active_by_hash(token_hash)

        if stored is None or not stored.is_active(now):
            raise AuthenticationError("Invalid or expired refresh token.")

        user = await self._users.get_by_id(stored.user_id)
        if user is None or not user.is_active:
            raise AuthenticationError("Account is no longer active.")

        # Issue the new pair first, then revoke the old token and link the
        # rotation chain (old -> newest refresh row).
        new_pair = await self._token_issuer.issue(
            user, user_agent=command.user_agent, ip_address=command.ip_address
        )
        new_hash = self._token_service.hash_refresh_token(new_pair.refresh_token)
        replacement = await self._refresh_tokens.get_active_by_hash(new_hash)
        await self._refresh_tokens.revoke(
            stored.id, replaced_by=replacement.id if replacement else None
        )
        return new_pair
