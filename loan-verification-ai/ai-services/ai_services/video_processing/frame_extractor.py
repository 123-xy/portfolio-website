"""Video frame extraction.

Default provider derives a plausible, reproducible frame set from the video
bytes without decoding (works on any input). The real provider (enabled via the
`real` extra) uses OpenCV to sample frames at a target FPS.
"""

from __future__ import annotations

from ai_services._determinism import stable_int
from ai_services.contracts import Frame


class DeterministicFrameExtractor:
    """Frame count scales with file size; timestamps are evenly spaced."""

    def __init__(self, min_frames: int = 4, max_frames: int = 30) -> None:
        self._min = min_frames
        self._max = max_frames

    def extract(self, video_bytes: bytes) -> list[Frame]:
        approx = max(self._min, min(self._max, len(video_bytes) // 50_000 or self._min))
        # Deterministic duration derived from the bytes (2–8 s per sampled frame).
        span_ms = 1000
        return [Frame(index=i, timestamp_ms=i * span_ms) for i in range(approx)]


def build_frame_extractor() -> DeterministicFrameExtractor:
    return DeterministicFrameExtractor()
