from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class OfficerDto:
    id: uuid.UUID
    user_id: uuid.UUID
    employee_code: str


class OfficerRepository(ABC):
    @abstractmethod
    async def get_by_user_id(self, user_id: uuid.UUID) -> OfficerDto | None:
        """The officer profile for a given user, if one exists. Officers are
        provisioned out-of-band (not self-registered); a signed-in user with
        role=officer but no profile row is a provisioning gap, not a normal
        state — callers treat None as an error."""
        ...
