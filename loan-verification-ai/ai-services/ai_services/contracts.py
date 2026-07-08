"""Typed inputs/outputs shared across the AI modules.

Pure dataclasses with no third-party dependencies, so every consumer (the
deterministic default providers here, and the backend orchestrator) speaks the
same language regardless of which model backend is active.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Frame:
    index: int
    timestamp_ms: int


@dataclass(frozen=True)
class FaceBox:
    frame_index: int
    x: float
    y: float
    width: float
    height: float
    confidence: float


@dataclass(frozen=True)
class FaceEmbedding:
    # L2-normalized vector; dimensionality depends on the backend.
    vector: tuple[float, ...]


@dataclass(frozen=True)
class MatchResult:
    similarity: float  # cosine similarity in [0, 1]
    is_match: bool


@dataclass(frozen=True)
class TranscriptSegment:
    start_ms: int
    end_ms: int
    text: str


@dataclass(frozen=True)
class Transcript:
    text: str
    language: str
    confidence: float
    segments: list[TranscriptSegment] = field(default_factory=list)


@dataclass(frozen=True)
class ConsentResult:
    # Mirrors the ConsentStatus enum values in the backend.
    status: str  # explicit_yes | ambiguous | explicit_no | not_detected
    confidence: float
    matched_phrases: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class IntentResult:
    aligned: bool
    confidence: float
    label: str
    reasons: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class FraudResult:
    # Higher score = more suspicious, in [0, 1].
    score: float
    confidence: float
    signals: list[str] = field(default_factory=list)
