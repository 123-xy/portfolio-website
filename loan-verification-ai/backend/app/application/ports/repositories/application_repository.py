from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from decimal import Decimal

from app.domain.entities.application import Application
from app.domain.value_objects.enums import ApplicationStatus


class ApplicationRepository(ABC):
    """Persistence port for applications and their co-applicant."""

    @abstractmethod
    async def next_reference_no(self) -> str:
        """Allocate the next human-facing reference number (concurrency-safe)."""
        ...

    @abstractmethod
    async def create(
        self,
        *,
        reference_no: str,
        applicant_id: uuid.UUID,
        loan_amount: Decimal,
        loan_purpose: str | None,
        co_applicant_full_name: str,
        co_applicant_relationship: str | None,
        co_applicant_email: str | None,
        co_applicant_phone: str | None,
    ) -> Application: ...

    @abstractmethod
    async def get_by_id(self, application_id: uuid.UUID) -> Application | None:
        """Load an application with its co-applicant and artifacts."""
        ...

    @abstractmethod
    async def list_for_applicant(self, applicant_id: uuid.UUID) -> list[Application]: ...

    @abstractmethod
    async def list_for_review(self) -> list[Application]:
        """Applications awaiting officer review (queue)."""
        ...

    @abstractmethod
    async def set_status(
        self,
        application_id: uuid.UUID,
        status: ApplicationStatus,
        *,
        mark_submitted: bool = False,
    ) -> None: ...
