"""Face detection over frames.

Default provider returns a reproducible bounding box per frame with a high
detection confidence. The real provider (OpenCV/MediaPipe) locates actual faces.
"""

from __future__ import annotations

from ai_services._determinism import float_in
from ai_services.contracts import FaceBox, Frame


class DeterministicFaceDetector:
    def detect(self, frames: list[Frame], seed: str) -> list[FaceBox]:
        boxes: list[FaceBox] = []
        for frame in frames:
            fseed = (seed, str(frame.index))
            boxes.append(
                FaceBox(
                    frame_index=frame.index,
                    x=float_in(0.2, 0.4, *fseed, "x"),
                    y=float_in(0.15, 0.35, *fseed, "y"),
                    width=float_in(0.2, 0.35, *fseed, "w"),
                    height=float_in(0.25, 0.4, *fseed, "h"),
                    confidence=float_in(0.86, 0.99, *fseed, "c"),
                )
            )
        return boxes


def build_face_detector() -> DeterministicFaceDetector:
    return DeterministicFaceDetector()
