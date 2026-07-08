from __future__ import annotations

from app.application.dto.risk import RiskInputs
from app.domain.value_objects.enums import VerificationStage


def _as_float(value: object) -> float | None:
    return value if isinstance(value, int | float) else None


def _as_str(value: object) -> str | None:
    return value if isinstance(value, str) else None


def _as_bool(value: object) -> bool | None:
    return value if isinstance(value, bool) else None


def build_risk_inputs(scalars: dict[VerificationStage, dict[str, object]]) -> RiskInputs:
    """Map the pipeline's latest per-stage scalar signals onto the risk
    engine's input shape. Missing stages (e.g. a partial/failed run) simply
    leave the corresponding fields None — the engine treats those neutrally
    and still reports why."""
    face = scalars.get(VerificationStage.FACE_MATCH, {})
    consent = scalars.get(VerificationStage.CONSENT_DETECTION, {})
    intent = scalars.get(VerificationStage.INTENT_ANALYSIS, {})
    fraud = scalars.get(VerificationStage.FRAUD_CHECK, {})

    intent_payload = intent.get("payload")
    fraud_payload = fraud.get("payload")
    intent_payload = intent_payload if isinstance(intent_payload, dict) else {}
    fraud_payload = fraud_payload if isinstance(fraud_payload, dict) else {}

    return RiskInputs(
        face_similarity=_as_float(face.get("similarity_score")),
        face_confidence=_as_float(face.get("confidence")),
        consent_status=_as_str(consent.get("consent")),
        consent_confidence=_as_float(consent.get("confidence")),
        intent_aligned=_as_bool(intent_payload.get("aligned")),
        intent_confidence=_as_float(intent.get("confidence")),
        fraud_score=_as_float(fraud_payload.get("fraud_score")),
        fraud_confidence=_as_float(fraud.get("confidence")),
    )
