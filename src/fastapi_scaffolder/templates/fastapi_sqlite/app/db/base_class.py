from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Shared declarative base for every ORM model in the project.
    All models should inherit from this class.
    """

    pass
