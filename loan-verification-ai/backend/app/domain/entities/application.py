from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from app.domain.value_objects.enums import ApplicationStatus


@dataclass
class CoApplicant:
    id: uuid.UUID
    full_name: str
    relationship_to_applicant: str | None = None
    email: str | None = None
    phone: str | None = None


@dataclass
class Artifact:
    id: uuid.UUID
    application_id: uuid.UUID
    kind: str
    status: str
    storage_key: str
    original_filename: str | None = None
    mime_type: str | None = None
    size_bytes: int | None = None
    checksum_sha256: str | None = None


@dataclass
class Application:
    id: uuid.UUID
    reference_no: str
    applicant_id: uuid.UUID
    loan_amount: Decimal
    status: ApplicationStatus
    loan_purpose: str | None = None
    submitted_at: datetime | None = None
    decided_at: datetime | None = None
    created_at: datetime | None = None
    co_applicant: CoApplicant | None = None
    artifacts: list[Artifact] = field(default_factory=list)
