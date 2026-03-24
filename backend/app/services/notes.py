from sqlalchemy.orm import Session

from app.models.product_note import ProductNote
from app.schemas.domain import ProductNoteCreate


def list_for_product(db: Session, product_id: int):
    return (
        db.query(ProductNote)
        .filter(ProductNote.product_id == product_id)
        .order_by(ProductNote.created_at.desc())
        .all()
    )


def create_note(db: Session, product_id: int, user_id: int, payload: ProductNoteCreate):
    note = ProductNote(product_id=product_id, created_by=user_id, **payload.model_dump())
    db.add(note)
    db.commit()
    db.refresh(note)
    return note
