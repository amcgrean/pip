from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.product_attachment import ProductAttachment
from app.models.user import User
from app.utils.deps import get_current_user

router = APIRouter(prefix="/attachments", tags=["attachments"])


@router.get("/")
def list_attachments(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rows = db.query(ProductAttachment).all()
    return [{"id": row.id, "product_id": row.product_id, "file_name": row.file_name, "file_path": row.file_path} for row in rows]
