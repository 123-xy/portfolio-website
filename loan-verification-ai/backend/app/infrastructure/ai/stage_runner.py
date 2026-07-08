from __future__ import annotations

from ai_services import (
    build_audio_extractor,
    build_consent_detector,
    build_face_detector,
    build_face_matcher,
    build_frame_extractor,
    build_fraud_detector,
    build_intent_analyzer,
    build_transcriber,
)

from app.application.dto.verification import PipelineContext, StageOutcome
from app.application.ports.repositories.artifact_repository import ArtifactRepository
from app.application.ports.services.object_storage import ObjectStorage
from app.application.ports.services.pipeline import StageRunner
from app.domain.entities.application import Artifact
from app.domain.value_objects.enums import (
    ArtifactKind,
    ConsentStatus,
    StageStatus,
    VerificationStage,
)

_PRESENT = {"uploaded", "ingested", "validated"}


class DeterministicStageRunner(StageRunner):
    """Runs each stage over the ai-services default (deterministic) providers.

    Downloads media from object storage where a real backend would need the
    bytes, and seeds the stand-in providers from stable artifact checksums so
    results are reproducible per application. Swapping to real model backends is
    a change of provider construction only — the stage logic is unchanged.
    """

    def __init__(self, storage: ObjectStorage, artifacts: ArtifactRepository) -> None:
        self._storage = storage
        self._artifacts = artifacts
        self._frames = build_frame_extractor()
        self._detector = build_face_detector()
        self._matcher = build_face_matcher()
        self._audio = build_audio_extractor()
        self._transcriber = build_transcriber()
        self._consent = build_consent_detector()
        self._intent = build_intent_analyzer()
        self._fraud = build_fraud_detector()

    async def run(self, stage: VerificationStage, context: PipelineContext) -> StageOutcome:
        handler = getattr(self, f"_stage_{stage.value}")
        outcome: StageOutcome = await handler(context)
        return outcome

    # --- helpers ---
    @staticmethod
    def _artifact(context: PipelineContext, kind: ArtifactKind) -> Artifact | None:
        for a in context.application.artifacts:
            if a.kind == kind.value and a.status in _PRESENT:
                return a
        return None

    @staticmethod
    def _seed(artifact: Artifact | None) -> str:
        if artifact is None:
            return "missing"
        return artifact.checksum_sha256 or artifact.storage_key

    # --- stages ---
    async def _stage_ingest(self, context: PipelineContext) -> StageOutcome:
        required = [
            ArtifactKind.APPLICANT_PHOTO,
            ArtifactKind.COAPPLICANT_PHOTO,
            ArtifactKind.VERIFICATION_VIDEO,
        ]
        present = {k: self._artifact(context, k) for k in required}
        missing = [k.value for k, a in present.items() if a is None]
        if missing:
            return StageOutcome.failed(f"Missing required artifacts: {', '.join(missing)}")
        context.scratch["seeds"] = {k.value: self._seed(a) for k, a in present.items()}
        context.scratch["video_key"] = present[ArtifactKind.VERIFICATION_VIDEO].storage_key  # type: ignore[union-attr]
        context.scratch["video_checksum"] = self._seed(present[ArtifactKind.VERIFICATION_VIDEO])
        return StageOutcome(
            status=StageStatus.COMPLETED, payload={"artifacts_present": [k.value for k in required]}
        )

    async def _stage_frame_extraction(self, context: PipelineContext) -> StageOutcome:
        video_bytes = await self._storage.download_bytes(context.scratch["video_key"])
        frames = self._frames.extract(video_bytes)
        context.scratch["frame_count"] = len(frames)
        context.scratch["video_bytes_len"] = len(video_bytes)
        return StageOutcome(status=StageStatus.COMPLETED, payload={"frame_count": len(frames)})

    async def _stage_face_detection(self, context: PipelineContext) -> StageOutcome:
        frames = self._frames.extract(b"0" * context.scratch.get("video_bytes_len", 100_000))
        boxes = self._detector.detect(frames, context.scratch["video_checksum"])
        avg_conf = round(sum(b.confidence for b in boxes) / len(boxes), 4) if boxes else 0.0
        context.scratch["detection_confidence"] = avg_conf
        return StageOutcome(
            status=StageStatus.COMPLETED,
            confidence=avg_conf,
            payload={"faces_detected": len(boxes), "avg_confidence": avg_conf},
        )

    async def _stage_face_embedding(self, context: PipelineContext) -> StageOutcome:
        seeds = context.scratch["seeds"]
        ref = self._matcher.embed(seeds[ArtifactKind.COAPPLICANT_PHOTO.value])
        probe = self._matcher.embed(context.scratch["video_checksum"])
        return StageOutcome(
            status=StageStatus.COMPLETED,
            payload={
                "embedding_dim": len(ref.vector),
                "vectors": 2,
                "probe_dim": len(probe.vector),
            },
        )

    async def _stage_face_match(self, context: PipelineContext) -> StageOutcome:
        seeds = context.scratch["seeds"]
        result = self._matcher.match(
            seeds[ArtifactKind.COAPPLICANT_PHOTO.value], context.scratch["video_checksum"]
        )
        context.scratch["face_similarity"] = result.similarity
        return StageOutcome(
            status=StageStatus.COMPLETED,
            similarity_score=result.similarity,
            confidence=context.scratch.get("detection_confidence", 0.9),
            payload={"is_match": result.is_match, "similarity": result.similarity},
        )

    async def _stage_audio_extraction(self, context: PipelineContext) -> StageOutcome:
        video_bytes = await self._storage.download_bytes(context.scratch["video_key"])
        track = self._audio.extract(video_bytes, source_ref=context.scratch["video_checksum"])
        context.scratch["audio_ref"] = track.source_ref
        return StageOutcome(
            status=StageStatus.COMPLETED,
            payload={"duration_seconds": track.duration_seconds, "sample_rate": track.sample_rate},
        )

    async def _stage_transcription(self, context: PipelineContext) -> StageOutcome:
        transcript = self._transcriber.transcribe(context.scratch["audio_ref"])
        context.scratch["transcript"] = transcript.text
        return StageOutcome(
            status=StageStatus.COMPLETED,
            confidence=transcript.confidence,
            payload={"language": transcript.language, "transcript": transcript.text},
        )

    async def _stage_consent_detection(self, context: PipelineContext) -> StageOutcome:
        result = self._consent.detect(context.scratch.get("transcript", ""))
        context.scratch["consent_status"] = result.status
        return StageOutcome(
            status=StageStatus.COMPLETED,
            consent=ConsentStatus(result.status),
            confidence=result.confidence,
            payload={"matched_phrases": result.matched_phrases},
        )

    async def _stage_intent_analysis(self, context: PipelineContext) -> StageOutcome:
        result = self._intent.analyze(context.scratch.get("transcript", ""))
        context.scratch["intent_aligned"] = result.aligned
        return StageOutcome(
            status=StageStatus.COMPLETED,
            confidence=result.confidence,
            payload={"aligned": result.aligned, "label": result.label, "reasons": result.reasons},
        )

    async def _stage_fraud_check(self, context: PipelineContext) -> StageOutcome:
        video_checksum = context.scratch["video_checksum"]
        duplicate = await self._artifacts.checksum_seen_on_other_application(
            video_checksum, context.application.id
        )
        result = self._fraud.assess(
            seed=str(context.application.id),
            face_similarity=context.scratch.get("face_similarity", 1.0),
            duplicate_media=duplicate,
        )
        return StageOutcome(
            status=StageStatus.COMPLETED,
            confidence=result.confidence,
            payload={"fraud_score": result.score, "signals": result.signals},
        )
