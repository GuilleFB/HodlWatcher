import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
os.environ.setdefault("DJANGO_CONFIGURATION", "Base")

from configurations import importer  # noqa

# Compatibility with django-configurations
from django.conf import settings  # noqa

importer.install()

app = Celery("HodlWatcher")
app.config_from_object("django.conf:settings")

# Autodiscover tasks for each integration
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
