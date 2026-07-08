from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from app.application.dto.reports import ReportDto
from app.domain.value_objects.enums import ReportFormat


class ReportRepository(ABC):
    @abstractmethod
    async def next_version(self, application_id: uuid.UUID | None, format: ReportFormat) -> int:
        """Next version number for this application+format (1-based); bulk
        exports (application_id=None) version against the format alone."""
        ...

    @abstractmethod
    async def create(
        self,
        *,
        application_id: uuid.UUID | None,
        format: ReportFormat,
        storage_key: str,
        generated_by: uuid.UUID,
        version: int,
    ) -> ReportDto: ...

    @abstractmethod
    async def get_by_id(self, report_id: uuid.UUID) -> ReportDto | None: ...
