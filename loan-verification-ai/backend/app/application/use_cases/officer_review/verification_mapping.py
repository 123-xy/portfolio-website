from __future__ import annotations

from app.application.dto.officer_review import VerificationDetails
from app.domain.value_objects.enums import VerificationStage


def _as_float(value: object) -> float | None:
    return value if isinstance(value, int | float) else None


def _as_str(value: object) -> str | None:
    return value if isinstance(value, str) else None


def _as_bool(value: object) -> bool | None:
    return value if isinstance(value, bool) else None


def _as_str_list(value: object) -> list[str]:
    return [v for v in value if isinstance(v, str)] if isinstance(value, list) else []


def _payload(stage_scalars: dict[str, object]) -> dict[str, object]:
    payload = stage_scalars.get("payload")
    return payload if isinstance(payload, dict) else {}


def build_verification_details(
    scalars: dict[VerificationStage, dict[str, object]],
) -> VerificationDetails:
    """Flattens the pipeline's latest per-stage scalars into the officer's
    evidence view. Pure mapping — shared by the review screen and report
    generation so both present identical evidence."""
    face = scalars.get(VerificationStage.FACE_MATCH, {})
    transcription = scalars.get(VerificationStage.TRANSCRIPTION, {})
    consent = scalars.get(VerificationStage.CONSENT_DETECTION, {})
    intent = scalars.get(VerificationStage.INTENT_ANALYSIS, {})
    fraud = scalars.get(VerificationStage.FRAUD_CHECK, {})

    transcription_payload = _payload(transcription)
    consent_payload = _payload(consent)
    intent_payload = _payload(intent)
    fraud_payload = _payload(fraud)

    return VerificationDetails(
        face_similarity=_as_float(face.get("similarity_score")),
        face_confidence=_as_float(face.get("confidence")),
        transcript_text=_as_str(transcription_payload.get("transcript")),
        transcript_language=_as_str(transcription_payload.get("language")),
        transcript_confidence=_as_float(transcription.get("confidence")),
        consent_status=_as_str(consent.get("consent")),
        consent_confidence=_as_float(consent.get("confidence")),
        consent_matched_phrases=_as_str_list(consent_payload.get("matched_phrases")),
        intent_aligned=_as_bool(intent_payload.get("aligned")),
        intent_confidence=_as_float(intent.get("confidence")),
        intent_label=_as_str(intent_payload.get("label")),
        intent_reasons=_as_str_list(intent_payload.get("reasons")),
        fraud_score=_as_float(fraud_payload.get("fraud_score")),
        fraud_confidence=_as_float(fraud.get("confidence")),
        fraud_signals=_as_str_list(fraud_payload.get("signals")),
    )
