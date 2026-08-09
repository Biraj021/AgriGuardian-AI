from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from typing import Generator
from src.core.config import settings
import sqlalchemy

_engine = None
SessionLocal = None


def get_engine():
    global _engine, SessionLocal
    if _engine is None:
        url = settings.DATABASE_URL
        # ensure sqlite has check_same_thread for threads used by FastAPI
        connect_args = {}
        if url.startswith("sqlite"):
            connect_args = {"check_same_thread": False}
        _engine = create_engine(url, connect_args=connect_args, future=True)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    return _engine


@contextmanager
def get_db() -> Generator:
    # create engine lazily to avoid running DB code at import time
    get_engine()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
