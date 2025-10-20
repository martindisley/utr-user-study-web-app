"""
Database initialization and management.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from backend.models import Base
from backend import config
import os


# Create engine
engine = create_engine(
    config.SQLALCHEMY_DATABASE_URI,
    echo=config.DEBUG,
    connect_args={'check_same_thread': False}  # Needed for SQLite
)

# Create session factory
SessionLocal = scoped_session(sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
))


def init_db():
    """Initialize the database, creating all tables."""
    # Ensure the data directory exists
    os.makedirs(os.path.dirname(config.DATABASE_PATH), exist_ok=True)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print(f"Database initialized at {config.DATABASE_PATH}")


def get_db():
    """Get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session():
    """Get a database session (non-generator version for route handlers)."""
    return SessionLocal()
