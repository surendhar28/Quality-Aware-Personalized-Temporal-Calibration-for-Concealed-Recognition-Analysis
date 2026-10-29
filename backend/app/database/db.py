"""
Database setup and connection management using SQLAlchemy and SQLite.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_PATH = os.environ.get("DATABASE_URL", "sqlite:///./backend/app/database/gazeguard.db")

# Ensure directory exists for sqlite file
if DB_PATH.startswith("sqlite:///"):
    raw_path = DB_PATH.replace("sqlite:///", "")
    os.makedirs(os.path.dirname(os.path.abspath(raw_path)), exist_ok=True)

engine = create_engine(
    DB_PATH,
    connect_args={"check_same_thread": False} if DB_PATH.startswith("sqlite") else {},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency for yielding database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)

# Auto-initialize on import so tables always exist
from . import models  # Ensure all models are registered on Base
init_db()
