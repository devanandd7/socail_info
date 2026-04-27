from apscheduler.schedulers.background import BackgroundScheduler

from models import db as models_db
from services.collector import collect_once
from services.config import settings

scheduler: BackgroundScheduler | None = None


def start_scheduler() -> None:
    global scheduler
    if scheduler is not None:
        return
    if models_db.db_config is None:
        raise RuntimeError("Database not initialized")

    scheduler = BackgroundScheduler(timezone="UTC")

    def _job() -> None:
        session = models_db.db_config.SessionLocal()
        try:
            collect_once(session)
        finally:
            session.close()

    scheduler.add_job(_job, "interval", minutes=settings.COLLECTION_INTERVAL_MINUTES, id="collect_posts")
    scheduler.start()


def stop_scheduler() -> None:
    global scheduler
    if scheduler is not None:
        scheduler.shutdown(wait=False)
        scheduler = None
