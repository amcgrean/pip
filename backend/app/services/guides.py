"""Service layer for Product Guide CRUD operations."""

import json

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.product import Product
from app.models.product_guide import ProductGuide, ProductGuideItem
from app.models.product_image import ProductImage


def list_guides(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
) -> tuple[list[dict], int]:
    """Return paginated list of guides with item counts."""
    query = db.query(
        ProductGuide,
        func.count(ProductGuideItem.id).label("item_count"),
    ).outerjoin(ProductGuideItem).group_by(ProductGuide.id)

    if search:
        query = query.filter(ProductGuide.name.ilike(f"%{search}%"))

    total = query.count()
    rows = (
        query.order_by(ProductGuide.updated_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    results = []
    for guide, item_count in rows:
        section_order = []
        if guide.section_order:
            try:
                section_order = json.loads(guide.section_order)
            except (json.JSONDecodeError, TypeError):
                pass
        results.append({
            "id": guide.id,
            "name": guide.name,
            "description": guide.description,
            "status": guide.status,
            "section_order": section_order,
            "item_count": item_count,
            "created_at": guide.created_at,
            "updated_at": guide.updated_at,
        })

    return results, total


def get_guide(db: Session, guide_id: int) -> dict | None:
    """Return full guide with items and flattened product info."""
    guide = db.query(ProductGuide).filter(ProductGuide.id == guide_id).first()
    if not guide:
        return None

    items = (
        db.query(ProductGuideItem)
        .options(joinedload(ProductGuideItem.product).joinedload(Product.images))
        .filter(ProductGuideItem.guide_id == guide_id)
        .order_by(ProductGuideItem.sort_order)
        .all()
    )

    section_order = []
    if guide.section_order:
        try:
            section_order = json.loads(guide.section_order)
        except (json.JSONDecodeError, TypeError):
            pass

    guide_out = {
        "id": guide.id,
        "name": guide.name,
        "description": guide.description,
        "status": guide.status,
        "section_order": section_order,
        "item_count": len(items),
        "created_at": guide.created_at,
        "updated_at": guide.updated_at,
    }

    items_out = []
    for item in items:
        p = item.product
        primary_image = None
        if p and p.images:
            sorted_imgs = sorted(p.images, key=lambda i: i.sort_order)
            primary_image = sorted_imgs[0].storage_path if sorted_imgs else None

        items_out.append({
            "id": item.id,
            "product_id": item.product_id,
            "section_name": item.section_name,
            "sort_order": item.sort_order,
            "override_description": item.override_description,
            "internal_sku": p.internal_sku if p else "",
            "normalized_name": p.normalized_name if p else "",
            "display_name": p.display_name if p else None,
            "thickness": p.thickness if p else None,
            "width": p.width if p else None,
            "length": p.length if p else None,
            "species_or_material": p.species_or_material if p else None,
            "profile": p.profile if p else None,
            "finish": p.finish if p else None,
            "category_major": p.category_major if p else None,
            "category_minor": p.category_minor if p else None,
            "primary_image_path": primary_image,
        })

    return {"guide": guide_out, "items": items_out}


def create_guide(db: Session, name: str, description: str | None = None, created_by: int | None = None) -> ProductGuide:
    """Create a new guide."""
    guide = ProductGuide(
        name=name,
        description=description,
        status="draft",
        section_order=json.dumps([]),
        created_by=created_by,
    )
    db.add(guide)
    db.commit()
    db.refresh(guide)
    return guide


def update_guide(db: Session, guide_id: int, data: dict) -> ProductGuide | None:
    """Update guide metadata."""
    guide = db.query(ProductGuide).filter(ProductGuide.id == guide_id).first()
    if not guide:
        return None

    if "name" in data and data["name"] is not None:
        guide.name = data["name"]
    if "description" in data and data["description"] is not None:
        guide.description = data["description"]
    if "status" in data and data["status"] is not None:
        guide.status = data["status"]
    if "section_order" in data and data["section_order"] is not None:
        guide.section_order = json.dumps(data["section_order"])

    db.commit()
    db.refresh(guide)
    return guide


def delete_guide(db: Session, guide_id: int) -> bool:
    """Delete a guide and all its items."""
    guide = db.query(ProductGuide).filter(ProductGuide.id == guide_id).first()
    if not guide:
        return False
    db.delete(guide)
    db.commit()
    return True


def add_item(
    db: Session,
    guide_id: int,
    product_id: int,
    section_name: str | None = None,
    sort_order: int = 0,
    override_description: str | None = None,
) -> ProductGuideItem | None:
    """Add a product to a guide. Returns None if already exists."""
    # Verify guide and product exist
    guide = db.query(ProductGuide).filter(ProductGuide.id == guide_id).first()
    if not guide:
        return None
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return None

    # Check for duplicate
    existing = (
        db.query(ProductGuideItem)
        .filter(
            ProductGuideItem.guide_id == guide_id,
            ProductGuideItem.product_id == product_id,
        )
        .first()
    )
    if existing:
        return existing

    # Auto-assign sort_order if not specified
    if sort_order == 0:
        max_order = (
            db.query(func.max(ProductGuideItem.sort_order))
            .filter(ProductGuideItem.guide_id == guide_id)
            .scalar()
        )
        sort_order = (max_order or 0) + 10

    # Auto-add section to section_order if new
    if section_name:
        section_order = []
        if guide.section_order:
            try:
                section_order = json.loads(guide.section_order)
            except (json.JSONDecodeError, TypeError):
                pass
        if section_name not in section_order:
            section_order.append(section_name)
            guide.section_order = json.dumps(section_order)

    item = ProductGuideItem(
        guide_id=guide_id,
        product_id=product_id,
        section_name=section_name,
        sort_order=sort_order,
        override_description=override_description,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def remove_item(db: Session, guide_id: int, item_id: int) -> bool:
    """Remove a product from a guide."""
    item = (
        db.query(ProductGuideItem)
        .filter(ProductGuideItem.id == item_id, ProductGuideItem.guide_id == guide_id)
        .first()
    )
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True


def bulk_reorder(db: Session, guide_id: int, items: list[dict]) -> bool:
    """Update sort_order and section_name for all items in a guide."""
    for item_data in items:
        item_id = item_data.get("id")
        if not item_id:
            continue
        item = (
            db.query(ProductGuideItem)
            .filter(ProductGuideItem.id == item_id, ProductGuideItem.guide_id == guide_id)
            .first()
        )
        if item:
            if "sort_order" in item_data:
                item.sort_order = item_data["sort_order"]
            if "section_name" in item_data:
                item.section_name = item_data["section_name"]
    db.commit()
    return True
