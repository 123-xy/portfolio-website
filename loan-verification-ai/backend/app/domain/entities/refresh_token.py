from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass
class RefreshToken:
    """Domain representation of a stored refresh token. Only the hash of the
    opaque token is ever persisted; the raw value exists briefly in memory."""

    id: uuid.UUID
    user_id: uuid.UUID
    token_hash: str
    expires_at: datetime
    revoked_at: datetime | None = None

    def is_active(self, now: datetime) -> bool:
        return self.revoked_at is None and self.expires_at > now
