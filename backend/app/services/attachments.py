from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.product_attachment import ProductAttachment
from app.services.storage import storage_service


def list_for_product(db: Session, product_id: int):
    return (
        db.query(ProductAttachment)
        .filter(ProductAttachment.product_id == product_id)
        .order_by(ProductAttachment.created_at.desc())
        .all()
    )


def create_attachment(db: Session, product_id: int, user_id: int, upload: UploadFile):
    suffix = Path(upload.filename or "").suffix.lower()
    if suffix not in settings.allowed_attachment_extensions_set:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")

    content = upload.file.read()
    if len(content) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty")
    if len(content) > settings.max_attachment_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds max size of {settings.max_attachment_size_bytes} bytes",
        )

    _, relative_path = storage_service.save_product_attachment(product_id=product_id, filename=upload.filename or "file", content=content)
    row = ProductAttachment(
        product_id=product_id,
        file_name=storage_service.sanitize_filename(upload.filename or "attachment"),
        file_path=relative_path,
        file_type=upload.content_type,
        uploaded_by=user_id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
