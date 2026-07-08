"""Reusable AI/ML inference modules for the co-applicant verification pipeline.

Each capability exposes a `build_*` factory returning the default (deterministic,
pure-Python) provider. Real model backends implement the same call shapes and
are swapped in by configuration, not by changing callers.
"""

from ai_services.audio_extraction.audio_extractor import build_audio_extractor
from ai_services.face_detection.detector import build_face_detector
from ai_services.face_recognition.matcher import build_face_matcher
from ai_services.fraud_detection.detector import build_fraud_detector
from ai_services.intent_detection.consent import build_consent_detector
from ai_services.intent_detection.intent import build_intent_analyzer
from ai_services.risk_engine.engine import build_risk_engine
from ai_services.speech_to_text.transcriber import build_transcriber
from ai_services.video_processing.frame_extractor import build_frame_extractor

__all__ = [
    "build_audio_extractor",
    "build_consent_detector",
    "build_face_detector",
    "build_face_matcher",
    "build_fraud_detector",
    "build_intent_analyzer",
    "build_risk_engine",
    "build_transcriber",
    "build_frame_extractor",
]
