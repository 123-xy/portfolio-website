from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from app.domain.value_objects.enums import DecisionType


@dataclass(frozen=True)
class VerificationDetails:
    """Consolidated pipeline evidence for the officer's review screen — one
    row per stage's latest scalars, flattened into the fields an officer
    actually needs to make a decision."""

    face_similarity: float | None
    face_confidence: float | None
    transcript_text: str | None
    transcript_language: str | None
    transcript_confidence: float | None
    consent_status: str | None
    consent_confidence: float | None
    consent_matched_phrases: list[str] = field(default_factory=list)
    intent_aligned: bool | None = None
    intent_confidence: float | None = None
    intent_label: str | None = None
    intent_reasons: list[str] = field(default_factory=list)
    fraud_score: float | None = None
    fraud_confidence: float | None = None
    fraud_signals: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RecordDecisionCommand:
    application_id: uuid.UUID
    decision: DecisionType
    reason: str


@dataclass(frozen=True)
class OfficerDecisionDto:
    id: uuid.UUID
    decision: DecisionType
    reason: str
    created_at: datetime


@dataclass(frozen=True)
class AuditEntryDto:
    id: uuid.UUID
    action: str
    actor_user_id: uuid.UUID | None
    is_system: bool
    target_type: str | None
    target_id: uuid.UUID | None
    metadata: dict[str, object] | None
    created_at: datetime
