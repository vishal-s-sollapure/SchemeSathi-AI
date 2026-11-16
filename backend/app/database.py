import os
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.base import Base

# Normalize database URL for PostgreSQL hosting (Render, Supabase, Neon)
raw_db_url = settings.DATABASE_URL
if raw_db_url.startswith("postgres://"):
    raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)

# Configure engine parameters depending on DB backend
connect_args = {}
engine_kwargs = {"echo": settings.DEBUG}

if raw_db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    engine_kwargs["connect_args"] = connect_args
    # Ensure directory exists if SQLite file is in a custom path (e.g. /var/data)
    if ":///" in raw_db_url:
        sqlite_path = raw_db_url.split(":///", 1)[1]
        if sqlite_path and not sqlite_path.startswith(":memory:"):
            parent_dir = Path(sqlite_path).parent
            if parent_dir and not parent_dir.exists():
                parent_dir.mkdir(parents=True, exist_ok=True)
else:
    # Production PostgreSQL connection pooling
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20
    engine_kwargs["pool_pre_ping"] = True

engine = create_engine(raw_db_url, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency to retrieve DB session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize all tables defined in models."""
    import app.models  # ensure all models are registered
    Base.metadata.create_all(bind=engine)

    # Lightweight schema migration for SQLite if existing local DB lacks newly added columns
    if raw_db_url.startswith("sqlite"):
        try:
            with engine.connect() as conn:
                res = conn.execute(text("PRAGMA table_info(uploaded_documents)")).fetchall()
                cols = {r[1] for r in res}
                if cols and "page_count" not in cols:
                    conn.execute(text("ALTER TABLE uploaded_documents ADD COLUMN page_count INTEGER DEFAULT 1"))
                if cols and "ocr_applied" not in cols:
                    conn.execute(text("ALTER TABLE uploaded_documents ADD COLUMN ocr_applied BOOLEAN DEFAULT 0"))
                if cols and "extra_metadata" not in cols:
                    conn.execute(text("ALTER TABLE uploaded_documents ADD COLUMN extra_metadata JSON DEFAULT '{}'"))
                conn.commit()
        except Exception:
            pass
