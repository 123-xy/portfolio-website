from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.repositories.refresh_token_repository import RefreshTokenRepository
from app.domain.entities.refresh_token import RefreshToken as RefreshTokenEntity
from app.infrastructure.db.models.refresh_token import RefreshToken as RefreshTokenModel


def _to_entity(model: RefreshTokenModel) -> RefreshTokenEntity:
    return RefreshTokenEntity(
        id=model.id,
        user_id=model.user_id,
        token_hash=model.token_hash,
        expires_at=model.expires_at,
        revoked_at=model.revoked_at,
    )


class SqlAlchemyRefreshTokenRepository(RefreshTokenRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        user_id: uuid.UUID,
        token_hash: str,
        expires_at: datetime,
        user_agent: str | None,
        ip_address: str | None,
    ) -> RefreshTokenEntity:
        model = RefreshTokenModel(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        self._session.add(model)
        await self._session.flush()
        return _to_entity(model)

    async def get_active_by_hash(self, token_hash: str) -> RefreshTokenEntity | None:
        result = await self._session.execute(
            select(RefreshTokenModel).where(
                RefreshTokenModel.token_hash == token_hash,
                RefreshTokenModel.revoked_at.is_(None),
            )
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def revoke(self, token_id: uuid.UUID, *, replaced_by: uuid.UUID | None = None) -> None:
        await self._session.execute(
            update(RefreshTokenModel)
            .where(RefreshTokenModel.id == token_id, RefreshTokenModel.revoked_at.is_(None))
            .values(revoked_at=datetime.now(UTC), replaced_by=replaced_by)
        )

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        await self._session.execute(
            update(RefreshTokenModel)
            .where(
                RefreshTokenModel.user_id == user_id,
                RefreshTokenModel.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(UTC))
        )
