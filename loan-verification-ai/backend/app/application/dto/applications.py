from __future__ import annotations

import uuid
from dataclasses import dataclass
from decimal import Decimal

from app.application.dto.risk import RiskScoreDto
from app.domain.entities.application import Application


@dataclass(frozen=True)
class CreateApplicationCommand:
    applicant_id: uuid.UUID
    loan_amount: Decimal
    loan_purpose: str | None
    co_applicant_full_name: str
    co_applicant_relationship: str | None
    co_applicant_email: str | None
    co_applicant_phone: str | None


@dataclass(frozen=True)
class InitUploadCommand:
    application_id: uuid.UUID
    kind: str
    content_type: str
    filename: str | None


@dataclass(frozen=True)
class UploadTicket:
    artifact_id: uuid.UUID
    upload_url: str
    storage_key: str
    max_size_bytes: int


@dataclass(frozen=True)
class ConfirmUploadCommand:
    application_id: uuid.UUID
    artifact_id: uuid.UUID


@dataclass(frozen=True)
class ApplicationWithRisk:
    """An application paired with its current risk score, if one has been
    computed. Kept as a wrapper rather than mutating the Application entity so
    the entity itself stays a pure reflection of the applications table."""

    application: Application
    risk: RiskScoreDto | None
