from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db

router = APIRouter(tags=["health"])


@router.get("/health/live")
def live_check():
    return {"status": "ok", "environment": settings.environment, "utc_time": datetime.now(timezone.utc)}


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connectivity check failed",
        ) from exc

    return {"status": "ok", "environment": settings.environment, "utc_time": datetime.now(timezone.utc)}


@router.get("/version")
def version_check():
    return {"name": settings.app_name, "version": settings.app_version, "environment": settings.environment}
