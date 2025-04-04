import os

from celery import Celery
from celery.schedules import crontab

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
    "update-prices-every-5-minutes": {
        "task": "main.tasks.update_price_cache",
        "schedule": 60 * 5,  # 5 minutos
    },
    "update-payment_methods-every-month": {
        "task": "main.tasks.update_payment_methods",
        "schedule": crontab(hour=4, minute=0, day_of_month=14),  # A las 4 AM cada día 14 del mes
    },
    "update-currencies-every-month": {
        "task": "main.tasks.update_currencies",
        "schedule": crontab(hour=4, minute=0, day_of_month=14),  # A las 4 AM cada día 14 del mes
    },
    "check-watchdogs-every-10-minutes": {
        "task": "main.tasks.check_watchdogs",
        "schedule": 60 * 10,  # Cada 10 minutos
    },
    "clean-old-notifications-daily": {
        "task": "main.tasks.clean_old_notifications",
        "schedule": crontab(hour=3, minute=0),  # A las 3 AM cada día
    },
    "update-offer-status-weekly": {
        "task": "main.tasks.update_offer_status",
        "schedule": crontab(hour=3, minute=0, day_of_week=0),  # Se ejecuta cada domingo a las 3:00 AM
    },
}
