# monitoring/ — Observability configuration

Prometheus + Grafana configuration for the platform. Run alongside the stack
with the monitoring overlay:

```bash
docker compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
```

- `prometheus/prometheus.yml` — scrape config. Scrapes the backend's `/metrics`
  endpoint (exposed via `prometheus-fastapi-instrumentator`): HTTP request
  rate, latency histogram, error rate, in-progress requests, all labelled by
  method / handler / status.
- `prometheus/alerts.yml` — alert rules: backend unreachable, elevated 5xx
  rate, high p95 latency.
- `grafana/provisioning/` — auto-provisions the Prometheus datasource so
  Grafana is usable on first boot.

## Status

Live for HTTP-level metrics (the backend instruments every request). The
pipeline-stage latency/failure and per-queue depth metrics envisioned in
Phase 2 §4.3 need the Celery worker to export its own metrics (e.g. a
`prometheus_client` pushgateway or a metrics exporter on the worker) — a
follow-up, since the worker is a task process without an HTTP surface to
scrape. The `detect_stuck_pipelines` beat job named there was never built (the
pipeline is a single synchronous Celery task; see docs/phase-14-docker.md), so
its stuck-job alert is intentionally absent.
