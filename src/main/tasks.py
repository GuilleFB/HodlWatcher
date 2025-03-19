import logging

from celery import shared_task


logger = logging.getLogger(__name__)


@shared_task()
def celery_hello(message="Hello Celery!"):
    logger.info(message)
    return {"message": message}
