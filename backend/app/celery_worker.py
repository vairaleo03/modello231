import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")

celery = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Europe/Rome",
    enable_utc=True,
    task_always_eager=False,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# Import esplicito dei task per forzarne la registrazione
from app.tasks import transcription_tasks


@celery.task
def test_task():
    print("task di test avviato")
    return "task completato con successo"

print("celeryconfigurato correttamente")
