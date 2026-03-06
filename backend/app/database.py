
"""Database engine, session, and dependency helpers."""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from backend.app.config import settings

# SQLite requires check_same_thread=False for multi-threaded request handling.
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

# The engine manages low-level DB connections using the configured URL.
engine = create_engine(settings.database_url, connect_args=connect_args)

# SessionLocal is used per-request to isolate transactions.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the parent class for all SQLAlchemy ORM models.
Base = declarative_base()


# FastAPI dependency that opens a DB session for a request and always closes it.
def get_db():
    # Create a new database session at request start.
    db: Session = SessionLocal()
    try:
        # Yield control back to FastAPI route handlers.
        yield db
    finally:
        # Close the session to release the DB connection.
        db.close()
