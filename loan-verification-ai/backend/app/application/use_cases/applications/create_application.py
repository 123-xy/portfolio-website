from __future__ import annotations

from app.application.dto.applications import CreateApplicationCommand
from app.application.ports.repositories.application_repository import ApplicationRepository
from app.domain.entities.application import Application


class CreateApplication:
    """Create a draft application with its co-applicant. The applicant then
    uploads artifacts and submits it for verification."""

    def __init__(self, applications: ApplicationRepository) -> None:
        self._applications = applications

    async def execute(self, command: CreateApplicationCommand) -> Application:
        reference_no = await self._applications.next_reference_no()
        return await self._applications.create(
            reference_no=reference_no,
            applicant_id=command.applicant_id,
            loan_amount=command.loan_amount,
            loan_purpose=command.loan_purpose,
            co_applicant_full_name=command.co_applicant_full_name,
            co_applicant_relationship=command.co_applicant_relationship,
            co_applicant_email=command.co_applicant_email,
            co_applicant_phone=command.co_applicant_phone,
        )
