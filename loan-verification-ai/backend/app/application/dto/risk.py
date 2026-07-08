from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class RiskInputs:
    """Signals extracted from the pipeline's verification_results, framework-
    independent — mirrors ai_services.risk_engine.RiskInputs so the
    infrastructure adapter maps 1:1 without lossy translation."""

    face_similarity: float | None = None
    face_confidence: float | None = None
    consent_status: str | None = None
    consent_confidence: float | None = None
    intent_aligned: bool | None = None
    intent_confidence: float | None = None
    fraud_score: float | None = None
    fraud_confidence: float | None = None


@dataclass(frozen=True)
class RiskAssessment:
    score: float
    band: str
    recommendation: str
    confidence: float
    component_scores: dict[str, float]
    reasons: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RiskEngineConfigDto:
    version: int
    weights: dict[str, float]
    thresholds: dict[str, float]


@dataclass(frozen=True)
class RiskScoreDto:
    id: uuid.UUID
    application_id: uuid.UUID
    score: float
    band: str
    recommendation: str
    confidence: float
    component_scores: dict[str, float]
    weights_snapshot: dict[str, float]
    reasons: list[str]
    created_at: datetime
