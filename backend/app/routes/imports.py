from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.domain import ImportJobListResponse, ImportJobOut, ImportSummary, PaginationMeta
from app.services import imports as import_service
from app.utils.deps import get_current_user

router = APIRouter(prefix="/imports", tags=["imports"])


@router.get("/jobs", response_model=ImportJobListResponse)
def list_import_jobs(page: int = 1, page_size: int = 20, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    items, total = import_service.list_jobs(db, page, page_size)
    return ImportJobListResponse(items=[ImportJobOut.model_validate(i) for i in items], meta=PaginationMeta(page=page, page_size=page_size, total=total))


def _read_csv_upload(file: UploadFile) -> bytes:
    suffix = (file.filename or "").lower().strip()
    if not suffix.endswith(".csv"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only .csv files are supported")

    content = file.file.read()
    if len(content) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded CSV is empty")
    if len(content) > settings.max_import_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CSV exceeds max size of {settings.max_import_size_bytes} bytes",
        )
    return content


@router.post("/products-csv", response_model=ImportSummary)
def upload_products_csv(file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    content = _read_csv_upload(file)
    job = import_service.process_product_csv_import(db, file.filename or "products_seed.csv", content, user.id)
    return ImportSummary(
        id=job.id,
        total_rows=job.total_rows,
        inserted=job.inserted_rows,
        updated=job.updated_rows,
        errored=job.error_rows,
        status=job.status,
    )


@router.post("/sheet-csv", response_model=ImportSummary)
def upload_sheet_csv(
    sheet_name: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    content = _read_csv_upload(file)
    try:
        job = import_service.process_sheet_csv_import(db, file.filename or f"{sheet_name}.csv", content, user.id, sheet_name=sheet_name)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return ImportSummary(
        id=job.id,
        total_rows=job.total_rows,
        inserted=job.inserted_rows,
        updated=job.updated_rows,
        errored=job.error_rows,
        status=job.status,
    )
