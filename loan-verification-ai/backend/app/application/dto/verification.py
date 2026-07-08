from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.domain.entities.application import Application
from app.domain.value_objects.enums import ConsentStatus, StageStatus


@dataclass
class StageOutcome:
    """Result of running one pipeline stage — persisted as a verification_results
    row and used to carry scalar signals forward."""

    status: StageStatus
    similarity_score: float | None = None
    confidence: float | None = None
    consent: ConsentStatus | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    error_reason: str | None = None

    @classmethod
    def skipped(cls, reason: str) -> StageOutcome:
        return cls(status=StageStatus.SKIPPED, payload={"reason": reason})

    @classmethod
    def failed(cls, reason: str) -> StageOutcome:
        return cls(status=StageStatus.FAILED, error_reason=reason)


@dataclass
class PipelineContext:
    """Shared state threaded through a single pipeline run. Stages read the
    application/artifacts and pass intermediate signals (transcript, face
    similarity, …) to later stages via `scratch`."""

    application: Application
    scratch: dict[str, Any] = field(default_factory=dict)
