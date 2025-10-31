"""Celery application for background tasks."""

from celery import Celery
import os

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "coding_agent",
    broker=redis_url,
    backend=redis_url
)

celery_app.conf.task_routes = {
    'workers.tasks.*': {'queue': 'default'},
}

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

