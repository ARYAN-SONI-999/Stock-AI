from celery import Celery

from app.core.config import settings

celery_app = Celery("stockmind_worker", broker=settings.redis_url, backend=settings.redis_url)


@celery_app.task
def ping() -> str:
    return "pong"
