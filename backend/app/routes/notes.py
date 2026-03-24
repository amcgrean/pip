from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.domain import ProductNoteCreate, ProductNoteOut
from app.services import notes as note_service
from app.utils.deps import get_current_user

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/product/{product_id}", response_model=list[ProductNoteOut])
def list_notes(product_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return [{**row.__dict__, "created_by_name": None} for row in note_service.list_for_product(db, product_id)]


@router.post("/product/{product_id}", response_model=ProductNoteOut, status_code=status.HTTP_201_CREATED)
def add_note(product_id: int, payload: ProductNoteCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = note_service.create_note(db, product_id, user.id, payload)
    return {**row.__dict__, "created_by_name": user.full_name}
