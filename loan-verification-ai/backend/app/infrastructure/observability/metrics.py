from __future__ import annotations

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator


def instrument_app(app: FastAPI, *, metrics_path: str = "/metrics") -> None:
    """Expose Prometheus metrics for the API.

    Adds default HTTP metrics (request count, latency histogram, in-progress
    gauge, request/response sizes) labelled by method, handler, and status,
    and mounts a scrape endpoint at ``metrics_path`` (top-level, outside the
    versioned API prefix, per Prometheus convention). Scraped by the
    Prometheus service in docker-compose.monitoring.yml.
    """
    Instrumentator(
        should_group_status_codes=True,
        # Don't let the scrape endpoint measure itself.
        excluded_handlers=[metrics_path],
    ).instrument(app).expose(app, endpoint=metrics_path, include_in_schema=False)
