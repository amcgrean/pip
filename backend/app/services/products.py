from sqlalchemy import asc, desc, func, or_
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.product_alias import ProductAlias
from app.models.product_attachment import ProductAttachment
from app.models.vendor_product_mapping import VendorProductMapping
from app.schemas.domain import ProductCreate, ProductUpdate

SORT_COLUMNS = {
    "internal_sku": Product.internal_sku,
    "normalized_name": Product.normalized_name,
    "status": Product.status,
    "category_major": Product.category_major,
    "product_type": Product.product_type,
    "created_at": Product.created_at,
    "updated_at": Product.updated_at,
}


def list_products(
    db: Session,
    page: int,
    page_size: int,
    search: str | None,
    vendor_id: int | None,
    category_major: str | None,
    category_minor: str | None,
    product_type: str | None,
    status: str | None,
    has_attachments: bool | None,
    sort_by: str,
    sort_dir: str,
):
    query = db.query(Product)
    if vendor_id:
        query = query.join(VendorProductMapping).filter(VendorProductMapping.vendor_id == vendor_id)
    search_term = (search or "").strip()
    if search_term:
        term = f"%{search_term}%"
        query = query.filter(
            or_(
                Product.internal_sku.ilike(term),
                Product.normalized_name.ilike(term),
                Product.description.ilike(term),
                Product.canonical_name.ilike(term),
                Product.display_name.ilike(term),
                Product.keywords.ilike(term),
                Product.search_text.ilike(term),
                Product.master_search_text.ilike(term),
                Product.aliases.any(ProductAlias.alias_text.ilike(term)),
            )
        )
    if category_major:
        query = query.filter(Product.category_major == category_major)
    if category_minor:
        query = query.filter(Product.category_minor == category_minor)
    if product_type:
        query = query.filter(Product.product_type == product_type)
    if status:
        query = query.filter(Product.status == status)
    if has_attachments is not None:
        if has_attachments:
            query = query.filter(Product.attachments.any())
        else:
            query = query.filter(~Product.attachments.any())

    total = query.distinct(Product.id).count()
    order_col = SORT_COLUMNS.get(sort_by, Product.normalized_name)
    ordered = desc(order_col) if sort_dir.lower() == "desc" else asc(order_col)
    rows = (
        query.distinct(Product.id)
        .order_by(ordered)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    attachment_counts = dict(
        db.query(ProductAttachment.product_id, func.count(ProductAttachment.id))
        .filter(ProductAttachment.product_id.in_([p.id for p in rows] or [0]))
        .group_by(ProductAttachment.product_id)
        .all()
    )
    for row in rows:
        setattr(row, "attachment_count", attachment_counts.get(row.id, 0))
    return rows, total


def create_product(db: Session, payload: ProductCreate):
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product: Product, payload: ProductUpdate):
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
