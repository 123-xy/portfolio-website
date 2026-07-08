from __future__ import annotations

from abc import ABC, abstractmethod

from app.application.dto.risk import RiskAssessment, RiskInputs


class RiskScoringService(ABC):
    """Port over the risk-scoring computation (pure, synchronous — no I/O)."""

    @abstractmethod
    def score(
        self, inputs: RiskInputs, weights: dict[str, float], thresholds: dict[str, float]
    ) -> RiskAssessment: ...
