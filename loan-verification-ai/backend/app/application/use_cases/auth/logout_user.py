from __future__ import annotations

from app.application.dto.auth import RefreshCommand
from app.application.ports.repositories.refresh_token_repository import RefreshTokenRepository
from app.application.ports.services.token_service import TokenService


class LogoutUser:
    """Revoke the presented refresh token. Idempotent — logging out with an
    already-invalid or unknown token is a no-op, never an error."""

    def __init__(
        self,
        refresh_tokens: RefreshTokenRepository,
        token_service: TokenService,
    ) -> None:
        self._refresh_tokens = refresh_tokens
        self._token_service = token_service

    async def execute(self, command: RefreshCommand) -> None:
        token_hash = self._token_service.hash_refresh_token(command.refresh_token)
        stored = await self._refresh_tokens.get_active_by_hash(token_hash)
        if stored is not None:
            await self._refresh_tokens.revoke(stored.id)
