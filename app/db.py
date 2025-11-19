"""
Database configuration and session management.

Provides SQLAlchemy engine, sessionmaker, and FastAPI dependency
for database session handling.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from app.config import get_settings


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
