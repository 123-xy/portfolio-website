from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Liveness — the process is up and serving."""

    status: Literal["ok"] = "ok"
    service: str = Field(examples=["AI Co-Applicant Verification Platform"])
    version: str = Field(examples=["0.1.0"])


class ComponentHealth(BaseModel):
    database: bool
    redis: bool


class ReadinessResponse(BaseModel):
    """Readiness — dependencies (DB, Redis) are reachable."""

    status: Literal["ready", "degraded"]
    components: ComponentHealth
