import httpx
import pytest

from app.main import create_app


@pytest.mark.asyncio
async def test_liveness_returns_ok() -> None:
    """Liveness must not depend on external services, so it is safe to assert
    without a database or Redis available."""
    app = create_app()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["version"]
    # request-id middleware must stamp every response.
    assert response.headers.get("x-request-id")


@pytest.mark.asyncio
async def test_metrics_endpoint_exposes_prometheus_data() -> None:
    """The /metrics endpoint (scraped by Prometheus in the monitoring stack)
    must serve Prometheus-format request metrics for the traffic it sees."""
    app = create_app()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        await client.get("/api/v1/health")
        response = await client.get("/metrics")

    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert "http_requests_total" in response.text
