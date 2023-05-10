from __future__ import absolute_import, unicode_literals
import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
# "sample_app" is name of the root app
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery(
    "celery_app", broker="redis://127.0.0.1:6379", backend="redis://127.0.0.1:6379"
)

# Load task modules from all registered Django apps.
app.autodiscover_tasks()