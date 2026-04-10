from collections.abc import Generator

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


def _build_engine():
    """Build the SQLAlchemy engine.

    If DB_HOST is set, use individual params (avoids URL-encoding issues
    with special characters in passwords). Otherwise, fall back to DATABASE_URL.
    """
    if settings.db_host:
        url = URL.create(
            drivername="postgresql+psycopg2",
            username=settings.db_user,
            password=settings.db_password,
            host=settings.db_host,
            port=settings.db_port,
            database=settings.db_name,
        )
        connect_args = {}
        if "pooler.supabase.com" in settings.db_host:
            connect_args["sslmode"] = "require"
        return create_engine(
            url, pool_pre_ping=True, pool_size=5, max_overflow=10,
            connect_args=connect_args,
        )
    return create_engine(settings.database_url, pool_pre_ping=True)


engine = _build_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
