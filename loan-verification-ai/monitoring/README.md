# monitoring/ — Observability configuration

Metrics, dashboards, and alert rules for the platform. Planned:

- Prometheus scrape config + service metrics (API latency, pipeline stage
  latency/failure rate, queue depth per Celery queue).
- Grafana dashboards (application volume, approval/rejection rates, risk
  trends, processing SLA).
- Alert rules: stuck pipelines past SLA, worker queue backlog, error-rate
  spikes, DB/Redis health.

The `detect_stuck_pipelines` beat job (Phase 2 §4.3) feeds the stuck-job
alert. Wired up in Phase 14/15.
