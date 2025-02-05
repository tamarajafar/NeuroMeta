from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from models import Base
import os

# Create database engine
DATABASE_URL = "sqlite:///brain_analysis.db"
engine = create_engine(DATABASE_URL)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize the database, creating tables only if they don't exist."""
    inspector = inspect(engine)

    # Check if tables already exist
    existing_tables = inspector.get_table_names()

    # Only create tables that don't exist
    if not existing_tables:
        Base.metadata.create_all(bind=engine)

def get_db():
    """Get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()