"""
FoodScout AI — Celery Worker Configuration
"""

from celery import Celery
from backend.config import get_settings

settings = get_settings()

celery_app = Celery(
    "foodscout",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["backend.workers.scan_worker"],
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
    result_expires=86400,  # 24 hours
    task_soft_time_limit=1800,  # 30 min soft
    task_time_limit=3600,  # 1 hr hard
    worker_max_tasks_per_child=50,
)
