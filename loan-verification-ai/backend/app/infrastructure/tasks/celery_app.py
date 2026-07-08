from celery import Celery

from app.core.config import get_settings

_settings = get_settings()

# Redis is both broker and result backend. Tasks are defined in
# pipeline_tasks (listed in `include` so the worker registers them).
celery_app = Celery(
    "verification",
    broker=str(_settings.redis_url),
    backend=str(_settings.redis_url),
    include=["app.infrastructure.tasks.pipeline_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)
