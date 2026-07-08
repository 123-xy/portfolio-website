"""Intent analysis — a real, deterministic rule classifier.

Checks whether the speaker's stated intent aligns with the loan co-applicant
context (understands the role, expresses willingness) rather than sounding
coerced, off-topic, or scripted-without-comprehension.
"""

from __future__ import annotations

import re

from ai_services.contracts import IntentResult

_CONTEXT_TERMS = [
    r"co-?applicant",
    r"\bloan\b",
    r"responsib",
    r"primary\s+applicant",
    r"guarantor",
    r"application",
]
_WILLINGNESS = [r"i\s+am\s+willing", r"i\s+agree", r"i\s+consent", r"i\s+confirm", r"i\s+accept"]
_COERCION = [r"told\s+to", r"asked\s+me\s+to", r"made\s+me", r"forced"]


def _count(patterns: list[str], text: str) -> int:
    return sum(1 for p in patterns if re.search(p, text))


class RuleBasedIntentAnalyzer:
    def analyze(self, transcript_text: str) -> IntentResult:
        text = transcript_text.lower()
        context = _count(_CONTEXT_TERMS, text)
        willingness = _count(_WILLINGNESS, text)
        coercion = _count(_COERCION, text)

        reasons: list[str] = []
        if context:
            reasons.append(f"References loan/co-applicant context ({context} cue(s))")
        if willingness:
            reasons.append(f"Expresses willingness ({willingness} cue(s))")
        if coercion:
            reasons.append(f"Possible coercion language ({coercion} cue(s))")

        aligned = context >= 1 and willingness >= 1 and coercion == 0
        if aligned:
            confidence = min(0.97, 0.72 + 0.08 * (context + willingness))
            label = "coapplicant_intent_confirmed"
        elif coercion and willingness:
            confidence = 0.5
            label = "willing_but_coercion_signal"
        elif context and not willingness:
            confidence = 0.45
            label = "context_without_willingness"
        else:
            confidence = 0.4
            label = "intent_unclear"

        return IntentResult(
            aligned=aligned, confidence=round(confidence, 4), label=label, reasons=reasons
        )


def build_intent_analyzer() -> RuleBasedIntentAnalyzer:
    return RuleBasedIntentAnalyzer()
