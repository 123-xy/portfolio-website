from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from app.domain.entities.user import User
from app.domain.value_objects.enums import UserRole


class UserRepository(ABC):
    """Persistence port for users. Returns domain entities, not ORM models."""

    @abstractmethod
    async def get_by_id(self, user_id: uuid.UUID) -> User | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def email_exists(self, email: str) -> bool: ...

    @abstractmethod
    async def create(
        self, *, email: str, full_name: str, password_hash: str, role: UserRole
    ) -> User: ...

    @abstractmethod
    async def update(self, user: User) -> None:
        """Persist mutable fields (login counters, lock, last_login)."""
        ...
