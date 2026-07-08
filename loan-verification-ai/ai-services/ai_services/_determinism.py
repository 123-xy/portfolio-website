"""Helpers for reproducible pseudo-outputs.

The default providers derive stable, reproducible values from input bytes so the
pipeline produces consistent, explainable results without heavy models — the
same input always yields the same output. These are stand-ins for real model
inference, isolated here so the seams are obvious.
"""

from __future__ import annotations

import hashlib
import math


def stable_int(*parts: bytes | str) -> int:
    h = hashlib.sha256()
    for part in parts:
        h.update(part.encode("utf-8") if isinstance(part, str) else part)
    return int.from_bytes(h.digest()[:8], "big")


def unit_float(*parts: bytes | str) -> float:
    """Deterministic float in [0, 1)."""
    return (stable_int(*parts) % 1_000_000) / 1_000_000.0


def float_in(lo: float, hi: float, *parts: bytes | str) -> float:
    return lo + (hi - lo) * unit_float(*parts)


def unit_vector(dim: int, *parts: bytes | str) -> tuple[float, ...]:
    """A deterministic L2-normalized vector of the given dimensionality."""
    values = [float_in(-1.0, 1.0, *parts, str(i)) for i in range(dim)]
    norm = math.sqrt(sum(v * v for v in values)) or 1.0
    return tuple(v / norm for v in values)
