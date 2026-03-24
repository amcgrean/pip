from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.product import Product
from app.models.user import User
from app.schemas.domain import PaginationMeta, ProductCreate, ProductDetailOut, ProductListResponse, ProductOut, ProductUpdate
from app.services import attachments as attachment_service
from app.services import mappings as mapping_service
from app.services import notes as note_service
from app.services import products as product_service
from app.utils.deps import get_current_user

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=ProductListResponse)
def list_products(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = None,
    vendor_id: int | None = None,
    category_major: str | None = None,
    category_minor: str | None = None,
    product_type: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    has_attachments: bool | None = None,
    sort_by: str = "normalized_name",
    sort_dir: str = "asc",
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    items, total = product_service.list_products(
        db,
        page,
        page_size,
        search,
        vendor_id,
        category_major,
        category_minor,
        product_type,
        status_filter,
        has_attachments,
        sort_by,
        sort_dir,
    )
    return ProductListResponse(items=[ProductOut.model_validate(p) for p in items], meta=PaginationMeta(page=page, page_size=page_size, total=total))


@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return product_service.create_product(db, payload)


@router.get("/{product_id}", response_model=ProductDetailOut)
def get_product_detail(product_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    mappings = mapping_service.list_for_product(db, product_id)
    attachments = attachment_service.list_for_product(db, product_id)
    notes = note_service.list_for_product(db, product_id)

    mapping_out = []
    for m in mappings:
        model = {**m.__dict__, "vendor_name": m.vendor.vendor_name if m.vendor else None, "vendor_code": m.vendor.vendor_code if m.vendor else None}
        mapping_out.append(model)

    attachment_out = [
        {**a.__dict__, "download_url": f"/api/v1/attachments/{a.id}/download"}
        for a in attachments
    ]
    note_out = [{**n.__dict__, "created_by_name": None} for n in notes]
    return {
        "product": product,
        "mappings": mapping_out,
        "attachments": attachment_out,
        "notes": note_out,
    }


@router.put("/{product_id}", response_model=ProductOut)
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product_service.update_product(db, product, payload)
