"""
Database initialization and session handling for Agricultural Disease Observation MVP.
Uses SQLite for local zero-configuration reproducibility.
Includes non-destructive additive migrations for Phase 2 schema extensions.
"""

from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

# Base directory paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR = DATA_DIR / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "agri_observation.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH.as_posix()}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency for obtaining database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Creates database tables if they do not exist and applies additive migrations."""
    from backend.app import models  # noqa: F401
    Base.metadata.create_all(bind=engine)

    # Phase 2.3 non-destructive schema migration: add environmental columns if missing
    env_columns = [
        ("rainfall_recent", "VARCHAR(32) DEFAULT 'Unknown'"),
        ("humidity_level", "VARCHAR(32) DEFAULT 'Unknown'"),
        ("temperature_band", "VARCHAR(32) DEFAULT 'Unknown'"),
        ("recent_weather_event", "VARCHAR(64) DEFAULT 'None'"),
        ("irrigation_status", "VARCHAR(32) DEFAULT 'Unknown'"),
        ("soil_moisture_observation", "VARCHAR(32) DEFAULT 'Unknown'"),
        ("field_condition", "VARCHAR(32) DEFAULT 'Unknown'")
    ]
    with engine.connect() as conn:
        for col_name, col_def in env_columns:
            try:
                conn.execute(text(f"ALTER TABLE cases ADD COLUMN {col_name} {col_def}"))
                conn.commit()
            except Exception:
                pass  # column already exists
