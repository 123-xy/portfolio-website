# ai-services/ — Reusable AI/ML inference package

Pure inference functions with no web framework and no database dependency.
Consumed by the backend's Celery workers as a **library** (not a separate
network service — see `../../docs/phase-2-architecture-design.md` §1 for
the rationale: the pipeline already crosses the API→worker process
boundary; a second network hop per stage would add latency and failure
modes without isolation benefit, since the worker container already
isolates these heavy dependencies from the API).

Each module is independent and reusable, exposing a narrow, typed
interface that the backend's `infrastructure/ai/*` adapters call. This
keeps the AI concerns swappable and unit-testable in isolation.

```
ai_services/
  face_detection/     # locate faces per frame (OpenCV / MediaPipe)
  face_recognition/   # embeddings + similarity (InsightFace)
  video_processing/   # frame extraction / sampling (FFmpeg)
  audio_extraction/   # pull audio track from video (FFmpeg)
  speech_to_text/     # transcription (Whisper)
  intent_detection/   # consent + intent classification (Gemini + deterministic fallback)
  fraud_detection/    # deepfake/replay heuristics, duplicate-face, frame consistency
  risk_engine/        # weighted composite scoring → band + recommendation + reasons
  report_generator/   # PDF / JSON / CSV report rendering
tests/                # per-module unit tests with fixture media
```

Design constraint: every function has a single responsibility, takes
plain inputs (paths/bytes/arrays), and returns plain typed outputs — no
hidden global state, so each module can be tested and scaled on its own.
