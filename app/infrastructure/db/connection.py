"""
Database configuration and session management.

Provides SQLAlchemy engine, sessionmaker, and FastAPI dependency
for database session handling.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from app.config.settings import get_settings


# Declarative base for ORM models
Base = declarative_base()


# Database engine
settings = get_settings()
engine = create_engine(settings.DB_URL, future=True, echo=False)


# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)


def init_db():
    """
    Initialize database by creating all tables if they don't exist.
    
    This function is idempotent and safe to call on every app startup.
    - If database file doesn't exist: creates it
    - If tables don't exist: creates them
    - If everything exists: does nothing
    """
    # Import models to register them with Base.metadata
    from app.infrastructure.db import models
    
    # Ensure data directory exists (for SQLite)
    if settings.DB_URL.startswith("sqlite:///"):
        db_path = settings.DB_URL.replace("sqlite:///", "")
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
    
    # Create all tables (idempotent - only creates if they don't exist)
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    FastAPI dependency that yields a database session.

    Yields:
        Session: SQLAlchemy database session

    Note:
        Ensures the session is properly closed after the request completes.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
