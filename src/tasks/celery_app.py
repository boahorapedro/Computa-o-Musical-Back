# src/tasks/celery_app.py
from celery import Celery
from src.config.settings import get_settings

settings = get_settings()

celery_app = Celery(
    "audio_mixer",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "src.tasks.separation",
        "src.tasks.analysis",
        "src.tasks.synthesis",
    ]
)

celery_app.conf.update(
    task_serializer='pickle',
    accept_content=['pickle', 'json'],
    result_serializer='pickle',
    task_track_started=True,
    task_time_limit=900,  # 15 min max
)
