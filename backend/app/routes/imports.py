from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.domain import ImportJobListResponse, ImportJobOut, ImportSummary, PaginationMeta, ScraperSyncRequest, ScraperSyncResponse
from app.services import imports as import_service
from app.services import scraper_sync as scraper_sync_service
from app.services import stock_import as stock_import_service
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


@router.post("/scraper-sync", response_model=ScraperSyncResponse)
def scraper_sync(
    payload: ScraperSyncRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Accept scraped product records, match to stock catalog, attach images."""
    import json as _json

    job = scraper_sync_service.process_scraper_sync(db, payload.records, user.id)

    # Parse the error_log JSON to extract detailed stats
    log_data = {}
    if job.error_log:
        try:
            log_data = _json.loads(job.error_log)
        except Exception:
            pass

    return ScraperSyncResponse(
        id=job.id,
        total_rows=job.total_rows,
        products_inserted=job.inserted_rows,
        products_updated=job.updated_rows,
        matched_to_stock=log_data.get("matched_to_stock", 0),
        images_inserted=log_data.get("images_inserted", 0),
        images_updated=log_data.get("images_updated", 0),
        errored=job.error_rows,
        status=job.status,
    )


def _read_xlsx_upload(file: UploadFile) -> bytes:
    suffix = (file.filename or "").lower().strip()
    if not suffix.endswith(".xlsx"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only .xlsx files are supported")

    content = file.file.read()
    if len(content) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")
    if len(content) > settings.max_import_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds max size of {settings.max_import_size_bytes} bytes",
        )
    return content


@router.post("/stock-catalog", response_model=ImportSummary)
def upload_stock_catalog(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    content = _read_xlsx_upload(file)
    job = stock_import_service.process_stock_catalog(
        db,
        file_content=content,
        file_name=file.filename or "stock_catalog.xlsx",
        user_id=user.id,
    )
    return ImportSummary(
        id=job.id,
        total_rows=job.total_rows,
        inserted=job.inserted_rows,
        updated=job.updated_rows,
        errored=job.error_rows,
        status=job.status,
    )
