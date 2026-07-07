from __future__ import annotations

import uuid

from sqlalchemy import exists, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.repositories.user_repository import UserRepository
from app.domain.entities.user import User as UserEntity
from app.domain.value_objects.enums import UserRole
from app.infrastructure.db.models.user import User as UserModel


def _to_entity(model: UserModel) -> UserEntity:
    return UserEntity(
        id=model.id,
        email=model.email,
        full_name=model.full_name,
        role=model.role,
        password_hash=model.password_hash,
        is_active=model.is_active,
        failed_login_count=model.failed_login_count,
        locked_until=model.locked_until,
        last_login_at=model.last_login_at,
    )


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: uuid.UUID) -> UserEntity | None:
        model = await self._session.get(UserModel, user_id)
        return _to_entity(model) if model else None

    async def get_by_email(self, email: str) -> UserEntity | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def email_exists(self, email: str) -> bool:
        result = await self._session.execute(
            select(exists().where(UserModel.email == email))
        )
        return bool(result.scalar())

    async def create(
        self, *, email: str, full_name: str, password_hash: str, role: UserRole
    ) -> UserEntity:
        model = UserModel(
            email=email,
            full_name=full_name,
            password_hash=password_hash,
            role=role,
        )
        self._session.add(model)
        # Flush to populate the server-generated id without ending the request
        # transaction (commit happens once at request end).
        await self._session.flush()
        return _to_entity(model)

    async def update(self, user: UserEntity) -> None:
        await self._session.execute(
            update(UserModel)
            .where(UserModel.id == user.id)
            .values(
                failed_login_count=user.failed_login_count,
                locked_until=user.locked_until,
                last_login_at=user.last_login_at,
                is_active=user.is_active,
            )
        )
