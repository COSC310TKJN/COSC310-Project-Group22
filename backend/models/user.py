
"""User ORM model used for authentication and authorization."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database import Base


# This model stores registered user accounts and role flags.
class User(Base):
    # Map this model to the users table.
    __tablename__ = "users"

    # Integer primary key for internal references.
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Unique username used during login and registration checks.
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

    # Securely hashed password (never store plain text passwords).
    hashed_password: Mapped[str] = mapped_column(String(512), nullable=False)

    # Canonical role stored as text to support role-based policy checks.
    role: Mapped[str] = mapped_column(String(20), default="user", nullable=False)

    # Role flag used later to distinguish manager and regular user permissions.
    is_manager: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Timestamp for account creation auditability.
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
