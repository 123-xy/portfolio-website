from __future__ import annotations

from ai_services import build_risk_engine
from ai_services.risk_engine.engine import RiskInputs as AiRiskInputs

from app.application.dto.risk import RiskAssessment, RiskInputs
from app.application.ports.services.risk_scoring import RiskScoringService


class AiServicesRiskScoringService(RiskScoringService):
    """Adapts the ai-services weighted risk engine to the application port."""

    def __init__(self) -> None:
        self._engine = build_risk_engine()

    def score(
        self, inputs: RiskInputs, weights: dict[str, float], thresholds: dict[str, float]
    ) -> RiskAssessment:
        result = self._engine.assess(
            AiRiskInputs(
                face_similarity=inputs.face_similarity,
                face_confidence=inputs.face_confidence,
                consent_status=inputs.consent_status,
                consent_confidence=inputs.consent_confidence,
                intent_aligned=inputs.intent_aligned,
                intent_confidence=inputs.intent_confidence,
                fraud_score=inputs.fraud_score,
                fraud_confidence=inputs.fraud_confidence,
            ),
            weights,
            thresholds,
        )
        return RiskAssessment(
            score=result.score,
            band=result.band,
            recommendation=result.recommendation,
            confidence=result.confidence,
            component_scores=result.component_scores,
            reasons=result.reasons,
        )
