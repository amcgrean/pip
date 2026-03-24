from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.product_attachment import ProductAttachment
from app.models.user import User
from app.schemas.domain import ProductAttachmentOut
from app.services import attachments as attachment_service
from app.services.storage import storage_service
from app.utils.deps import get_current_user

router = APIRouter(prefix="/attachments", tags=["attachments"])


@router.get("/product/{product_id}", response_model=list[ProductAttachmentOut])
def list_attachments(product_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rows = attachment_service.list_for_product(db, product_id)
    return [{**row.__dict__, "download_url": f"/api/v1/attachments/{row.id}/download"} for row in rows]


@router.post("/product/{product_id}", response_model=ProductAttachmentOut, status_code=status.HTTP_201_CREATED)
def upload_attachment(
    product_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = attachment_service.create_attachment(db, product_id, user.id, file)
    return {**row.__dict__, "download_url": f"/api/v1/attachments/{row.id}/download"}


@router.get("/{attachment_id}/download")
def download_attachment(attachment_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    row = db.query(ProductAttachment).filter(ProductAttachment.id == attachment_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Attachment not found")

    candidate = Path(row.file_path)
    file_path = candidate if candidate.is_absolute() else (storage_service.root / candidate)
    resolved = file_path.resolve()
    if not str(resolved).startswith(str(storage_service.root)):
        raise HTTPException(status_code=400, detail="Invalid attachment path")
    if not resolved.exists():
        raise HTTPException(status_code=404, detail="Attachment file not found")
    return FileResponse(path=str(resolved), filename=row.file_name)
