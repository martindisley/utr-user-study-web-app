"""
Database initialization and management.
"""
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, scoped_session
from backend.models import Base
from backend import config
import os
from functools import wraps
from flask import jsonify


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


def with_db_session(func):
    """Decorator that provides and manages a database session for a route handler."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        db = get_db_session()
        try:
            return func(*args, db=db, **kwargs)
        except Exception as e:
            db.rollback()
            raise
        finally:
            db.close()
    return wrapper


def init_db():
    """Initialize the database, creating all tables."""
    # Ensure the data directory exists
    os.makedirs(os.path.dirname(config.DATABASE_PATH), exist_ok=True)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)

    _run_migrations()
    print(f"Database initialized at {config.DATABASE_PATH}")


def _run_migrations():
    """Apply lightweight schema migrations for new columns."""
    inspector = inspect(engine)
    if 'sessions' not in inspector.get_table_names():
        return

    session_columns = {col['name'] for col in inspector.get_columns('sessions')}
    if 'context_reset_at' not in session_columns:
        with engine.begin() as connection:
            connection.execute(text('ALTER TABLE sessions ADD COLUMN context_reset_at DATETIME'))
            connection.execute(text('UPDATE sessions SET context_reset_at = created_at WHERE context_reset_at IS NULL'))


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
