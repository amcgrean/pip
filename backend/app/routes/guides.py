"""API routes for Product Guide management and PDF generation."""

import json

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io

from app.db.session import get_db
from app.models.user import User
from app.schemas.domain import (
    GuideBulkReorderRequest,
    GuideCreate,
    GuideDetailOut,
    GuideItemCreate,
    GuideItemOut,
    GuideListResponse,
    GuideOut,
    GuideUpdate,
    PaginationMeta,
)
from app.services import guides as guide_service
from app.services.pdf_guide import generate_guide_pdf
from app.utils.deps import get_current_user

router = APIRouter(prefix="/guides", tags=["guides"])


@router.get("/", response_model=GuideListResponse)
def list_guides(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = None,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    results, total = guide_service.list_guides(db, page=page, page_size=page_size, search=search)
    return GuideListResponse(
        items=[GuideOut(**r) for r in results],
        meta=PaginationMeta(page=page, page_size=page_size, total=total),
    )


@router.post("/", response_model=GuideOut, status_code=status.HTTP_201_CREATED)
def create_guide(
    payload: GuideCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    guide = guide_service.create_guide(db, name=payload.name, description=payload.description, created_by=user.id)
    return GuideOut(
        id=guide.id,
        name=guide.name,
        description=guide.description,
        status=guide.status,
        section_order=[],
        item_count=0,
        created_at=guide.created_at,
        updated_at=guide.updated_at,
    )


@router.get("/{guide_id}", response_model=GuideDetailOut)
def get_guide(
    guide_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    result = guide_service.get_guide(db, guide_id)
    if not result:
        raise HTTPException(status_code=404, detail="Guide not found")
    return GuideDetailOut(
        guide=GuideOut(**result["guide"]),
        items=[GuideItemOut(**i) for i in result["items"]],
    )


@router.put("/{guide_id}", response_model=GuideOut)
def update_guide(
    guide_id: int,
    payload: GuideUpdate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    data = payload.model_dump(exclude_unset=True)
    guide = guide_service.update_guide(db, guide_id, data)
    if not guide:
        raise HTTPException(status_code=404, detail="Guide not found")

    section_order = []
    if guide.section_order:
        try:
            section_order = json.loads(guide.section_order)
        except (json.JSONDecodeError, TypeError):
            pass

    return GuideOut(
        id=guide.id,
        name=guide.name,
        description=guide.description,
        status=guide.status,
        section_order=section_order,
        item_count=len(guide.items),
        created_at=guide.created_at,
        updated_at=guide.updated_at,
    )


@router.delete("/{guide_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_guide(
    guide_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    if not guide_service.delete_guide(db, guide_id):
        raise HTTPException(status_code=404, detail="Guide not found")


@router.post("/{guide_id}/items", response_model=GuideItemOut, status_code=status.HTTP_201_CREATED)
def add_item_to_guide(
    guide_id: int,
    payload: GuideItemCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    item = guide_service.add_item(
        db,
        guide_id=guide_id,
        product_id=payload.product_id,
        section_name=payload.section_name,
        sort_order=payload.sort_order,
        override_description=payload.override_description,
    )
    if not item:
        raise HTTPException(status_code=404, detail="Guide or product not found")

    # Re-fetch with product data for response
    result = guide_service.get_guide(db, guide_id)
    if result:
        for i in result["items"]:
            if i["id"] == item.id:
                return GuideItemOut(**i)

    # Fallback minimal response
    return GuideItemOut(
        id=item.id,
        product_id=item.product_id,
        section_name=item.section_name,
        sort_order=item.sort_order,
        override_description=item.override_description,
    )


@router.delete("/{guide_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_item_from_guide(
    guide_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    if not guide_service.remove_item(db, guide_id, item_id):
        raise HTTPException(status_code=404, detail="Item not found")


@router.put("/{guide_id}/items/reorder")
def reorder_items(
    guide_id: int,
    payload: GuideBulkReorderRequest,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    guide_service.bulk_reorder(db, guide_id, payload.items)
    return {"status": "ok"}


@router.get("/{guide_id}/pdf")
def download_guide_pdf(
    guide_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    pdf_bytes = generate_guide_pdf(db, guide_id)
    if pdf_bytes is None:
        raise HTTPException(status_code=404, detail="Guide not found")

    # Get the guide name for the filename
    result = guide_service.get_guide(db, guide_id)
    filename = "Product_Guide.pdf"
    if result:
        safe_name = result["guide"]["name"].replace(" ", "_").replace("/", "-")
        filename = f"{safe_name}.pdf"

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
