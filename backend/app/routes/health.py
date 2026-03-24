from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "environment": settings.environment, "utc_time": datetime.now(timezone.utc)}


@router.get("/version")
def version_check():
    return {"name": settings.app_name, "version": settings.app_version, "environment": settings.environment}
