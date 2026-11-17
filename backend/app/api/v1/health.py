from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal, get_db

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check(db: Optional[Session] = Depends(get_db)):
    """Returns application and database connectivity health status."""
    db_status = "healthy"
    try:
        if isinstance(db, Session):
            db.execute(text("SELECT 1"))
        else:
            with SessionLocal() as session:
                session.execute(text("SELECT 1"))
    except Exception as exc:
        db_status = f"unhealthy: {str(exc)}"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "application": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }

