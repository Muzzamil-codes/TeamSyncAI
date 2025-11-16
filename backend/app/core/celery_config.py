"""
Celery configuration for background task processing
"""
import logging
import os
from dotenv import load_dotenv

# Suppress Redis connection warnings BEFORE importing Celery
logging.getLogger('celery').setLevel(logging.WARNING)
logging.getLogger('celery.backends').setLevel(logging.CRITICAL)
logging.getLogger('celery.brokers').setLevel(logging.CRITICAL)

from celery import Celery
from celery.schedules import crontab

load_dotenv()

# Celery configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "teamsync",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes hard limit
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    broker_connection_retry_on_startup=False,  # Don't retry at startup
    broker_connection_retry=False,  # Don't retry connections
    task_acks_late=True,  # Acknowledge task after execution
)

# Periodic tasks (if needed)
celery_app.conf.beat_schedule = {
    "cleanup-old-tasks": {
        "task": "app.tasks.cleanup_old_files",
        "schedule": crontab(hour=2, minute=0),  # 2 AM daily
    },
}
