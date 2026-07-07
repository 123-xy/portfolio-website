from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from app.domain.value_objects.enums import UserRole


@dataclass
class User:
    """Domain representation of a user, independent of persistence. Repositories
    map between this and the ORM model so use cases never import SQLAlchemy."""

    id: uuid.UUID
    email: str
    full_name: str
    role: UserRole
    password_hash: str
    is_active: bool = True
    failed_login_count: int = 0
    locked_until: datetime | None = None
    last_login_at: datetime | None = None

    def is_locked(self, now: datetime) -> bool:
        return self.locked_until is not None and self.locked_until > now
