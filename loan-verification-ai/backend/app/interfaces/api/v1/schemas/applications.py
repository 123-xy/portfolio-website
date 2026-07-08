from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field

from app.domain.value_objects.enums import ApplicationStatus, ArtifactKind, RiskBand


class CoApplicantInput(BaseModel):
    full_name: str = Field(min_length=2, max_length=200)
    relationship: str | None = Field(default=None, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=40)


class CreateApplicationRequest(BaseModel):
    loan_amount: Decimal = Field(gt=0, le=Decimal("999999999999"))
    loan_purpose: str | None = Field(default=None, max_length=500)
    co_applicant: CoApplicantInput


class CoApplicantResponse(BaseModel):
    id: uuid.UUID
    full_name: str
    relationship: str | None
    email: str | None
    phone: str | None


class ArtifactResponse(BaseModel):
    id: uuid.UUID
    kind: ArtifactKind
    status: str
    mime_type: str | None
    size_bytes: int | None
    original_filename: str | None


class RiskScoreResponse(BaseModel):
    score: Decimal
    band: RiskBand
    recommendation: str
    confidence: Decimal
    component_scores: dict[str, float]
    reasons: list[str]


class ApplicationResponse(BaseModel):
    id: uuid.UUID
    reference_no: str
    loan_amount: Decimal
    loan_purpose: str | None
    status: ApplicationStatus
    submitted_at: datetime | None
    decided_at: datetime | None
    created_at: datetime | None
    co_applicant: CoApplicantResponse | None
    artifacts: list[ArtifactResponse]
    risk: RiskScoreResponse | None = None


class ApplicationSummaryResponse(BaseModel):
    """Lightweight list item — omits artifact detail."""

    id: uuid.UUID
    reference_no: str
    loan_amount: Decimal
    status: ApplicationStatus
    co_applicant_name: str | None
    submitted_at: datetime | None
    created_at: datetime | None
    risk_band: RiskBand | None = None


class InitUploadRequest(BaseModel):
    kind: ArtifactKind
    content_type: str = Field(min_length=1, max_length=100)
    filename: str | None = Field(default=None, max_length=255)


class InitUploadResponse(BaseModel):
    artifact_id: uuid.UUID
    upload_url: str
    storage_key: str
    max_size_bytes: int


class ConfirmUploadRequest(BaseModel):
    artifact_id: uuid.UUID
