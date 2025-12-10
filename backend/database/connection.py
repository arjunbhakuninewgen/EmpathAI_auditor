# backend/database/connection.py
"""
Database connection using SQLAlchemy + Neon PostgreSQL
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
import os
from dotenv import load_dotenv

load_dotenv()

# Neon PostgreSQL connection (with SSL)
DATABASE_URL = os.getenv("DATABASE_URL")

# Use NullPool for serverless (Neon)
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    echo=False  # Set to True for SQL debugging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency for FastAPI to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables (run once)."""
    from . import models  # Import models to register them
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created!")
