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

# Schedule tasks
app.conf.beat_schedule = {
    "celery-hello-every-1-minute": {
        "task": "main.tasks.celery_hello",
        "schedule": 60 * 60 * 1,  # 1 horas
    },
    "update-prices-every-5-minutes": {
        "task": "main.tasks.update_price_cache",
        "schedule": 60 * 5,  # 5 minutos
    },
    "update-payment_methods-every-1-day": {
        "task": "main.tasks.update_payment_methods",
        "schedule": 60 * 60 * 24 * 1,  # 1 día
    },
}
