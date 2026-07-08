from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.value_objects.enums import DecisionType


class VerificationDetailsResponse(BaseModel):
    face_similarity: float | None
    face_confidence: float | None
    transcript_text: str | None
    transcript_language: str | None
    transcript_confidence: float | None
    consent_status: str | None
    consent_confidence: float | None
    consent_matched_phrases: list[str]
    intent_aligned: bool | None
    intent_confidence: float | None
    intent_label: str | None
    intent_reasons: list[str]
    fraud_score: float | None
    fraud_confidence: float | None
    fraud_signals: list[str]


class ArtifactDownloadResponse(BaseModel):
    download_url: str


class DecisionRequest(BaseModel):
    decision: DecisionType
    reason: str = Field(min_length=1, max_length=2000)


class DecisionResponse(BaseModel):
    id: uuid.UUID
    decision: DecisionType
    reason: str
    created_at: datetime


class AuditEntryResponse(BaseModel):
    id: uuid.UUID
    action: str
    actor_user_id: uuid.UUID | None
    is_system: bool
    target_type: str | None
    target_id: uuid.UUID | None
    metadata: dict[str, object] | None
    created_at: datetime
