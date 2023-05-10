from __future__ import absolute_import, unicode_literals
import os
from datetime import datetime, timedelta
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# TODO: switch to environment variables
app = Celery(
    "celery_app", broker="redis://127.0.0.1:6379", backend="redis://127.0.0.1:6379"
)

# set the schedule in seconds
schedule = [
    30,
    45,
    60,
    120,
    180,
    300,
    600,
    900,
    1800,
]

# schedule the task
for sec in schedule:
    app.conf.beat_schedule[f"task_{sec}"] = {
        "task": "logger.tasks.prepare_logs",
        "schedule": timedelta(seconds=sec),
        "args": (sec,),
    }
# Load task modules from all registered Django apps.
app.autodiscover_tasks()
