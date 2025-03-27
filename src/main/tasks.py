import logging
from alertas_bot.views import BuscadorView
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task()
def celery_hello(message="Hello Celery!"):
    logger.info(message)
    return {"message": message}


@shared_task
def update_price_cache():
    currencies = ["EUR", "USD"]  # Divisas soportadas
    view = BuscadorView()
    for currency in currencies:
        view.get_average_price(currency)


@shared_task
def update_payment_methods():
    view = BuscadorView()
    view._cached_payment_methods()
