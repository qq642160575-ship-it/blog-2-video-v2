#!/usr/bin/env python3
"""
Database initialization script
Creates all tables using SQLAlchemy models
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.db import engine, Base
from app.models import Project, GenerationJob, Scene


def init_db():
    """Create all tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully!")
    print("\nCreated tables:")
    print("  - projects")
    print("  - generation_jobs")
    print("  - scenes")


if __name__ == "__main__":
    init_db()
