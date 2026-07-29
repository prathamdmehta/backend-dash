from app.db.base import Base  # noqa: F401  (pulls in all models)
from app.db.session import engine


def init_db() -> None:
    """
    Create all tables that don't exist yet.
    Fine for SQLite/dev. In a real project you'd swap this for
    Alembic migrations once the schema stabilizes.
    """
    Base.metadata.create_all(bind=engine)
