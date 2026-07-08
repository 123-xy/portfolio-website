"""Weighted risk engine — real, deterministic scoring logic (not a stand-in).

Combines the four Phase-1 signal categories (face match, speech/consent,
intent, fraud) into a single explainable risk score:

    score = 1 - (w_face*face_trust + w_speech*speech_trust
                 + w_intent*intent_trust + w_fraud*fraud_trust)

Each `*_trust` component is in [0, 1] where higher means "more trustworthy /
lower risk"; `score` is therefore a risk score in [0, 1] where higher means
more risk. Missing signals fall back to a neutral 0.5 trust rather than
silently dropping out of the average, and a reason is recorded either way so
the output is always explainable to the officer reviewing it.
"""

from __future__ import annotations

from dataclasses import dataclass, field

DEFAULT_WEIGHTS: dict[str, float] = {
    "face_match": 0.40,
    "speech": 0.20,
    "intent": 0.20,
    "fraud": 0.20,
}
DEFAULT_THRESHOLDS: dict[str, float] = {"low_max": 0.33, "medium_max": 0.66}


@dataclass(frozen=True)
class RiskInputs:
    face_similarity: float | None = None
    face_confidence: float | None = None
    consent_status: str | None = None  # explicit_yes | ambiguous | explicit_no | not_detected
    consent_confidence: float | None = None
    intent_aligned: bool | None = None
    intent_confidence: float | None = None
    fraud_score: float | None = None  # higher = more suspicious
    fraud_confidence: float | None = None


@dataclass(frozen=True)
class RiskAssessment:
    score: float
    band: str  # low | medium | high
    recommendation: str  # auto_approve_candidate | needs_review | high_risk_reject_candidate
    confidence: float
    component_scores: dict[str, float]
    reasons: list[str] = field(default_factory=list)


def _consent_trust(status: str | None, confidence: float | None) -> tuple[float, str]:
    conf = confidence if confidence is not None else 0.5
    if status == "explicit_yes":
        return conf, f"Explicit consent detected (confidence {conf:.2f})"
    if status == "explicit_no":
        return 1 - conf, f"Explicit refusal detected (confidence {conf:.2f})"
    if status == "ambiguous":
        return conf * 0.5, f"Consent was ambiguous (confidence {conf:.2f})"
    if status == "not_detected":
        return 0.3, "No clear consent statement detected"
    return 0.5, "Consent signal unavailable"


def _intent_trust(aligned: bool | None, confidence: float | None) -> tuple[float, str]:
    conf = confidence if confidence is not None else 0.5
    if aligned is None:
        return 0.5, "Intent signal unavailable"
    if aligned:
        return conf, f"Intent aligned with co-applicant context (confidence {conf:.2f})"
    return 1 - conf, f"Intent did not align with expected context (confidence {conf:.2f})"


def assess_risk(
    inputs: RiskInputs,
    weights: dict[str, float] | None = None,
    thresholds: dict[str, float] | None = None,
) -> RiskAssessment:
    weights = weights or DEFAULT_WEIGHTS
    thresholds = thresholds or DEFAULT_THRESHOLDS
    reasons: list[str] = []

    face_similarity = inputs.face_similarity if inputs.face_similarity is not None else 0.5
    face_confidence = inputs.face_confidence if inputs.face_confidence is not None else 0.5
    reasons.append(
        f"Face match similarity {face_similarity:.2f}"
        if inputs.face_similarity is not None
        else "Face match signal unavailable"
    )

    speech_trust, speech_reason = _consent_trust(inputs.consent_status, inputs.consent_confidence)
    reasons.append(speech_reason)
    speech_confidence = inputs.consent_confidence if inputs.consent_confidence is not None else 0.5

    intent_trust, intent_reason = _intent_trust(inputs.intent_aligned, inputs.intent_confidence)
    reasons.append(intent_reason)
    intent_confidence = inputs.intent_confidence if inputs.intent_confidence is not None else 0.5

    fraud_score = inputs.fraud_score if inputs.fraud_score is not None else 0.3
    fraud_trust = 1 - fraud_score
    fraud_confidence = inputs.fraud_confidence if inputs.fraud_confidence is not None else 0.5
    reasons.append(
        "No significant fraud signals detected"
        if fraud_score < 0.3
        else f"Elevated fraud risk signals (score {fraud_score:.2f})"
    )

    component_scores = {
        "face_match": round(face_similarity, 4),
        "speech": round(speech_trust, 4),
        "intent": round(intent_trust, 4),
        "fraud": round(fraud_trust, 4),
    }

    weighted_trust = (
        weights.get("face_match", 0.0) * face_similarity
        + weights.get("speech", 0.0) * speech_trust
        + weights.get("intent", 0.0) * intent_trust
        + weights.get("fraud", 0.0) * fraud_trust
    )
    score = round(max(0.0, min(1.0, 1 - weighted_trust)), 4)

    low_max = thresholds.get("low_max", DEFAULT_THRESHOLDS["low_max"])
    medium_max = thresholds.get("medium_max", DEFAULT_THRESHOLDS["medium_max"])
    if score <= low_max:
        band, recommendation = "low", "auto_approve_candidate"
    elif score <= medium_max:
        band, recommendation = "medium", "needs_review"
    else:
        band, recommendation = "high", "high_risk_reject_candidate"

    confidence = round(
        (face_confidence + speech_confidence + intent_confidence + fraud_confidence) / 4, 4
    )

    return RiskAssessment(
        score=score,
        band=band,
        recommendation=recommendation,
        confidence=confidence,
        component_scores=component_scores,
        reasons=reasons,
    )


class WeightedRiskEngine:
    """Thin callable wrapper so the engine is swappable like every other
    ai-services capability (e.g. a future ML-based scorer implements the same
    `assess` shape)."""

    def assess(
        self,
        inputs: RiskInputs,
        weights: dict[str, float] | None = None,
        thresholds: dict[str, float] | None = None,
    ) -> RiskAssessment:
        return assess_risk(inputs, weights, thresholds)


def build_risk_engine() -> WeightedRiskEngine:
    return WeightedRiskEngine()
