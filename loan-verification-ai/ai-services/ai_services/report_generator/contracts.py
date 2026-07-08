"""Typed inputs for report rendering — framework-independent, no DB/ORM
dependency, so the same data can be assembled by the backend and handed to
any renderer (PDF/JSON/CSV) here."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class DecisionRecord:
    decision: str
    reason: str
    created_at: datetime


@dataclass(frozen=True)
class RiskSummary:
    score: float
    band: str
    recommendation: str
    confidence: float
    component_scores: dict[str, float]
    reasons: list[str]


@dataclass(frozen=True)
class EvidenceSummary:
    face_similarity: float | None
    consent_status: str | None
    intent_aligned: bool | None
    fraud_score: float | None


@dataclass(frozen=True)
class ApplicationReportData:
    """Everything needed to render a single application's report."""

    reference_no: str
    status: str
    loan_amount: str  # pre-formatted currency string (currency choice is a presentation concern)
    loan_purpose: str | None
    co_applicant_name: str | None
    submitted_at: datetime | None
    decided_at: datetime | None
    risk: RiskSummary | None
    evidence: EvidenceSummary | None
    decisions: list[DecisionRecord] = field(default_factory=list)
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    generated_by: str = ""


@dataclass(frozen=True)
class BulkExportRow:
    """One row of the compliance bulk export."""

    reference_no: str
    status: str
    loan_amount: str
    co_applicant_name: str | None
    risk_band: str | None
    risk_score: float | None
    submitted_at: datetime | None
    decided_at: datetime | None
