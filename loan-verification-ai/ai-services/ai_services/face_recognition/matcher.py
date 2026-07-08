"""Face embedding + matching.

Default provider produces reproducible embeddings and a deterministic similarity
in a realistic band, so downstream risk scoring sees a meaningful spread across
applications. The real provider (InsightFace) embeds actual faces and compares
by cosine similarity — the same interface and the same MatchResult output.
"""

from __future__ import annotations

from ai_services._determinism import float_in, unit_vector
from ai_services.contracts import FaceEmbedding, MatchResult

_EMBEDDING_DIM = 128
_MATCH_THRESHOLD = 0.62


class DeterministicFaceMatcher:
    def embed(self, seed: str) -> FaceEmbedding:
        return FaceEmbedding(vector=unit_vector(_EMBEDDING_DIM, seed))

    def match(self, reference_seed: str, probe_seed: str) -> MatchResult:
        """Compare a reference face (ID photo) to a probe face (from the video).

        The stand-in similarity is a stable function of both inputs spanning a
        realistic range (0.45–0.98); a real backend would compute the cosine of
        the two embeddings. Either way the output is a MatchResult the pipeline
        treats identically.
        """
        similarity = round(float_in(0.45, 0.98, reference_seed, probe_seed), 4)
        return MatchResult(similarity=similarity, is_match=similarity >= _MATCH_THRESHOLD)


def build_face_matcher() -> DeterministicFaceMatcher:
    return DeterministicFaceMatcher()
