from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class DBConfig:
    def __init__(self, database_url: str) -> None:
        connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
        self.engine = create_engine(database_url, connect_args=connect_args)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)


db_config: DBConfig | None = None


def init_db(database_url: str) -> None:
    global db_config
    db_config = DBConfig(database_url)


def create_tables() -> None:
    if db_config is None:
        raise RuntimeError("Database not initialized")
    Base.metadata.create_all(bind=db_config.engine)


def get_db() -> Generator:
    if db_config is None:
        raise RuntimeError("Database not initialized")
    db = db_config.SessionLocal()
    try:
        yield db
    finally:
        db.close()
