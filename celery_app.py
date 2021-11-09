from connections import get_celery_app


celery_app = get_celery_app(__name__)
celery_app.conf.beat_schedule = {
    "process-lend-every-20-seconds": {
        "task": "lend.lend",
        "schedule": 20.0,
    },
    "process-new": {
        "task": "rent.new_ads",
        "schedule": 300.0,
    },
    "process-upped": {
        "task": "rent.upped_ads",
        "schedule": 270.0,
    },
}
