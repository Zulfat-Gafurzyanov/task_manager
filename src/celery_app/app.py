from celery import Celery
from celery.schedules import crontab
from kombu import Queue

from src.core.config import settings

app = Celery(
    "src.celery_app.app",
    broker=settings.RABBIT_AMQP,
    backend="rpc://",
    include=["src.celery_app.celery_tasks"],
)

app.conf.task_queues = (
    Queue("emails.welcome"),
    Queue("emails.scheduled"),
)

app.conf.beat_schedule = {
    "send-planned-email-every-day": {
        "task": "src.celery_app.celery_tasks.send_planned_email",
        "schedule": crontab(minute="*/5"),
        "options": {"expires": 270},  # 4.5 минуты в секундах
    },
}

# Запуск воркера:  celery --app src.celery_app.app worker --pool solo --loglevel=INFO
# Запуск beat:     celery --app src.celery_app.app beat --loglevel=INFO
# Пересобрать: docker compose up -d --build celery-worker celery-beat
# Стоп: docker compose stop celery-beat celery-worker
# Старт: docker compose start celery-beat celery-worker
# Логи: docker logs task_manager-celery-worker-1 --tail 20
