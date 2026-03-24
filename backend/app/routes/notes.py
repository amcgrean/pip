from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.product_note import ProductNote
from app.models.user import User
from app.utils.deps import get_current_user

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/")
def list_notes(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rows = db.query(ProductNote).all()
    return [{"id": row.id, "product_id": row.product_id, "note_type": row.note_type} for row in rows]
