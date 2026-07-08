"""Audio extraction from the verification video.

Default provider reports a reproducible duration and passes the source reference
through; the real provider (FFmpeg) demuxes the audio track to a wav/pcm buffer.
"""

from __future__ import annotations

from dataclasses import dataclass

from ai_services._determinism import float_in


@dataclass(frozen=True)
class AudioTrack:
    duration_seconds: float
    sample_rate: int
    source_ref: str


class DeterministicAudioExtractor:
    def extract(self, video_bytes: bytes, source_ref: str) -> AudioTrack:
        duration = round(float_in(6.0, 40.0, source_ref, str(len(video_bytes))), 1)
        return AudioTrack(duration_seconds=duration, sample_rate=16_000, source_ref=source_ref)


def build_audio_extractor() -> DeterministicAudioExtractor:
    return DeterministicAudioExtractor()
