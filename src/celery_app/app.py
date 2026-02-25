import os

from celery import Celery
from dotenv import load_dotenv

load_dotenv()

app = Celery(
    "src.celery_app.app",
    broker=os.environ["RABBITMQ_URL"],
    backend="rpc://",
    include=["src.celery_app.celery_tasks"],
)

# celery --app celery_app.app worker --pool solo --loglevel=INFO