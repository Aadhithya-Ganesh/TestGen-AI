from celery import Celery
import os

app = Celery(
    "worker",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND"),
)

app.conf.update(
    task_track_started=True,
)

from app.tasks.workflow import *
