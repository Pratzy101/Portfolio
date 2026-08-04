"""
Database connection setup.

Three things are defined here:
  engine       — the actual connection to the database
  SessionLocal — a factory that hands out short-lived sessions (one per request)
  Base         — the parent class every table model inherits from
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

# SQLite has a threading restriction that doesn't apply to other databases.
# This argument disables it, which is required because FastAPI handles
# requests across multiple threads.
connect_args = (
    {"check_same_thread": False}
    if settings.DATABASE_URL.startswith("sqlite")
    else {}
)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    # Reconnects automatically if a pooled connection has gone stale —
    # matters on hosted Postgres, harmless on SQLite.
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """All table models inherit from this."""


def get_db():
    """
    FastAPI dependency.

    Opens a database session for a single request and guarantees it is
    closed afterwards, even if the request raises an error. Any endpoint
    that needs the database declares `db: Session = Depends(get_db)` and
    FastAPI calls this for it.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Creates any tables that don't exist yet.

    Fine for a project this size. Once the schema starts changing after
    real data exists, this gets replaced with Alembic migrations.
    """
    # Importing models registers them on Base.metadata before create_all runs.
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
