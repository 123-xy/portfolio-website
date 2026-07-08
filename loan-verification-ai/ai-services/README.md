# ai-services/ — Reusable AI/ML inference package

Pure inference modules for the verification pipeline, with **no web framework
and no database dependency**. Consumed by the backend's Celery workers as a
library (see `../../docs/phase-2-architecture-design.md` §1).

## Design

Each capability exposes a `build_*()` factory returning the **default provider**
— deterministic, pure-Python, and dependency-light, so the pipeline runs
anywhere (CI, laptops, this environment). Real model backends implement the same
call shapes and are enabled via the `real` extra and configuration — swapping
them is a config change, not a code change.

```
ai_services/
  contracts.py          # shared dataclasses (Frame, MatchResult, Transcript, …)
  video_processing/     # frame extraction         (default: size-derived; real: OpenCV)
  face_detection/       # face localization        (default: reproducible boxes; real: MediaPipe)
  face_recognition/     # embeddings + matching    (default: deterministic similarity; real: InsightFace)
  audio_extraction/     # audio track              (default: metadata; real: FFmpeg)
  speech_to_text/       # transcription            (default: consent scripts; real: Whisper)
  intent_detection/     # consent + intent         (REAL rule/keyword classifiers — auditable)
  fraud_detection/      # anomaly/fraud scoring     (heuristic + real signals from the orchestrator)
```

### What is real vs. stand-in

- **Consent and intent detection are genuine implementations** — deterministic
  rule/keyword classifiers over the transcript. Per the Phase 1 design these are
  the *auditable system of record*; an LLM (Gemini) can be layered on as
  advisory input, but the rules are always authoritative and inspectable.
- **Face matching** exposes real cosine-similarity math; the default seeds it
  from stable checksums to yield a realistic, reproducible spread without heavy
  models.
- **Frame/face/audio/transcription front-ends** use deterministic stand-ins for
  the heavy models (InsightFace/Whisper/OpenCV), isolated behind `build_*`
  factories so the real backends drop in unchanged.

## Usage

```python
from ai_services import build_consent_detector, build_face_matcher

consent = build_consent_detector().detect("I agree and I give my full consent")
# ConsentResult(status="explicit_yes", confidence=0.98, matched_phrases=[...])

match = build_face_matcher().match(reference_seed, probe_seed)
# MatchResult(similarity=0.72, is_match=True)
```

## Install

```bash
pip install -e .            # default deterministic providers
pip install -e ".[real]"   # + OpenCV/numpy for real backends (where supported)
```
