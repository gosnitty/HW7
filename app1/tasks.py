from celery_config import make_celery
from main import app

celery = make_celery(app)

@celery.task(bind=True)
def process_task(self, data):
    """Приклад довгої задачі для Celery"""
    import time
    result = f"Processing {data}"
    time.sleep(5)  # Імітація довгої операції
    return result