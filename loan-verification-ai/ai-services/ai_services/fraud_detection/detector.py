"""Fraud / anomaly detection.

Combines available signals into a fraud score (higher = more suspicious). The
default provider computes deterministic anomaly signals and folds in real
signals passed by the orchestrator (e.g. a low face-match similarity, or a
duplicate media checksum seen on another application). Real deepfake/replay
detectors slot in behind the same interface.
"""

from __future__ import annotations

from ai_services._determinism import float_in
from ai_services.contracts import FraudResult


class HeuristicFraudDetector:
    def assess(
        self,
        *,
        seed: str,
        face_similarity: float,
        duplicate_media: bool,
    ) -> FraudResult:
        signals: list[str] = []
        score = float_in(0.02, 0.2, seed, "base-anomaly")  # low baseline noise

        # A weak face match is itself a fraud signal (possible impersonation).
        if face_similarity < 0.55:
            score += 0.45
            signals.append("low_face_match_similarity")
        elif face_similarity < 0.7:
            score += 0.15
            signals.append("moderate_face_match_similarity")

        # The same media reused across applications is a strong signal.
        if duplicate_media:
            score += 0.5
            signals.append("duplicate_media_checksum")

        # A deterministic replay/deepfake heuristic stand-in.
        replay = float_in(0.0, 1.0, seed, "replay-heuristic")
        if replay > 0.9:
            score += 0.25
            signals.append("replay_artifact_suspected")

        score = round(min(score, 1.0), 4)
        return FraudResult(score=score, confidence=0.8, signals=signals)


def build_fraud_detector() -> HeuristicFraudDetector:
    return HeuristicFraudDetector()
