"""Speech-to-text.

Default provider returns one of several realistic consent scripts, chosen
deterministically from the audio reference, so the (real, rule-based)
consent/intent detectors downstream have varied natural-language input. The real
provider (Whisper) transcribes the actual audio to the same Transcript shape.
"""

from __future__ import annotations

from ai_services._determinism import float_in, unit_float
from ai_services.contracts import Transcript, TranscriptSegment

_CLEAR_CONSENT = (
    "Hello, my name is the co-applicant for this loan application. "
    "I confirm that I have reviewed the loan details and I agree to be a "
    "co-applicant. I give my full consent and I am willing to take on this "
    "responsibility together with the primary applicant."
)
_AMBIGUOUS = (
    "Um, I think so. My relative asked me to record this. I am not completely "
    "sure what being a co-applicant involves, but I suppose that is okay."
)
_EXPLICIT_NO = (
    "I was told to record this message, but I do not agree to this. I do not "
    "consent to being a co-applicant for this loan."
)


class DeterministicTranscriber:
    def transcribe(self, audio_ref: str) -> Transcript:
        bucket = unit_float(audio_ref, "consent-bucket")
        if bucket < 0.12:
            text, conf = _EXPLICIT_NO, float_in(0.70, 0.85, audio_ref)
        elif bucket < 0.28:
            text, conf = _AMBIGUOUS, float_in(0.60, 0.80, audio_ref)
        else:
            text, conf = _CLEAR_CONSENT, float_in(0.85, 0.98, audio_ref)

        return Transcript(
            text=text,
            language="en",
            confidence=round(conf, 4),
            segments=[TranscriptSegment(start_ms=0, end_ms=len(text) * 60, text=text)],
        )


def build_transcriber() -> DeterministicTranscriber:
    return DeterministicTranscriber()
