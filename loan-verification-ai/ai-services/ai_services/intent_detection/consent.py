"""Consent detection — a real, deterministic rule/keyword classifier.

This is the auditable system-of-record layer from the Phase 1 design: an
explainable classifier over the transcript. An optional LLM (Gemini) can be
layered on top as advisory input, but this rule engine is always authoritative
and fully inspectable.
"""

from __future__ import annotations

import re

from ai_services.contracts import ConsentResult

# Ordered by precedence — an explicit refusal outranks an affirmation.
_NEGATIVE = [
    r"do(?:es)?\s+not\s+consent",
    r"don'?t\s+consent",
    r"do(?:es)?\s+not\s+agree",
    r"don'?t\s+agree",
    r"i\s+refuse",
    r"i\s+disagree",
    r"not\s+willing",
]
_AFFIRMATIVE = [
    r"i\s+agree",
    r"i\s+consent",
    r"give\s+(?:my\s+)?(?:full\s+)?consent",
    r"i\s+am\s+willing",
    r"i\s+confirm",
    r"i\s+accept",
]
_HEDGE = [r"i\s+think\s+so", r"not\s+sure", r"i\s+suppose", r"i\s+guess", r"maybe", r"i\s+assume"]


def _matches(patterns: list[str], text: str) -> list[str]:
    found: list[str] = []
    for pattern in patterns:
        m = re.search(pattern, text)
        if m:
            found.append(m.group(0))
    return found


class RuleBasedConsentDetector:
    def detect(self, transcript_text: str) -> ConsentResult:
        text = transcript_text.lower()
        negatives = _matches(_NEGATIVE, text)
        if negatives:
            return ConsentResult(status="explicit_no", confidence=0.9, matched_phrases=negatives)

        affirmatives = _matches(_AFFIRMATIVE, text)
        hedges = _matches(_HEDGE, text)

        if affirmatives and not hedges:
            # Confidence grows with the number of distinct affirmations.
            confidence = min(0.98, 0.7 + 0.1 * len(affirmatives))
            return ConsentResult(
                status="explicit_yes", confidence=round(confidence, 4), matched_phrases=affirmatives
            )
        if affirmatives and hedges:
            return ConsentResult(
                status="ambiguous", confidence=0.55, matched_phrases=affirmatives + hedges
            )
        if hedges:
            return ConsentResult(status="ambiguous", confidence=0.5, matched_phrases=hedges)
        return ConsentResult(status="not_detected", confidence=0.4, matched_phrases=[])


def build_consent_detector() -> RuleBasedConsentDetector:
    return RuleBasedConsentDetector()
