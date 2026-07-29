from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Nullable because Google-only users never set a password.
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Set when the user signed up (or linked) via Google.
    google_sub: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True, index=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
