from __future__ import annotations

from abc import ABC, abstractmethod

from app.application.dto.risk import RiskEngineConfigDto


class RiskEngineConfigRepository(ABC):
    @abstractmethod
    async def get_active(self) -> RiskEngineConfigDto:
        """The currently active weights/thresholds. Exactly one row is active
        at a time (enforced by a partial unique index); seeded by migration."""
        ...
