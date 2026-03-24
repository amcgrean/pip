from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.import_job import ImportJob
from app.models.user import User
from app.schemas.domain import ImportJobOut
from app.utils.deps import get_current_user

router = APIRouter(prefix="/imports", tags=["imports"])


@router.get("/jobs", response_model=list[ImportJobOut])
def list_import_jobs(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(ImportJob).order_by(ImportJob.created_at.desc()).all()
