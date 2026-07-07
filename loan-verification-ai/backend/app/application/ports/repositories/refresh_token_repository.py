from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.entities.refresh_token import RefreshToken


class RefreshTokenRepository(ABC):
    """Persistence port for refresh tokens (stored hashed)."""

    @abstractmethod
    async def create(
        self,
        *,
        user_id: uuid.UUID,
        token_hash: str,
        expires_at: datetime,
        user_agent: str | None,
        ip_address: str | None,
    ) -> RefreshToken: ...

    @abstractmethod
    async def get_active_by_hash(self, token_hash: str) -> RefreshToken | None: ...

    @abstractmethod
    async def revoke(
        self, token_id: uuid.UUID, *, replaced_by: uuid.UUID | None = None
    ) -> None: ...

    @abstractmethod
    async def revoke_all_for_user(self, user_id: uuid.UUID) -> None: ...
