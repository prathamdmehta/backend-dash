from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# check_same_thread is only needed for SQLite; harmless to leave the
# kwarg conditional so this file works unchanged if you switch DBs.
connect_args = (
    {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    """
    FastAPI dependency that yields a DB session and guarantees it's
    closed afterwards, even if the request raises.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
