from sqlalchemy.orm import Session, joinedload

from app.models.vendor_product_mapping import VendorProductMapping
from app.schemas.domain import VendorMappingCreate, VendorMappingUpdate


def list_for_product(db: Session, product_id: int):
    return (
        db.query(VendorProductMapping)
        .options(joinedload(VendorProductMapping.vendor))
        .filter(VendorProductMapping.product_id == product_id)
        .order_by(VendorProductMapping.is_primary.desc(), VendorProductMapping.vendor_sku.asc())
        .all()
    )


def _unset_primary(db: Session, mapping: VendorProductMapping):
    if mapping.is_primary:
        (
            db.query(VendorProductMapping)
            .filter(
                VendorProductMapping.product_id == mapping.product_id,
                VendorProductMapping.id != mapping.id,
            )
            .update({"is_primary": False})
        )


def create_mapping(db: Session, payload: VendorMappingCreate):
    mapping = VendorProductMapping(**payload.model_dump())
    db.add(mapping)
    db.flush()
    _unset_primary(db, mapping)
    db.commit()
    db.refresh(mapping)
    return mapping


def update_mapping(db: Session, mapping: VendorProductMapping, payload: VendorMappingUpdate):
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(mapping, key, value)
    db.add(mapping)
    db.flush()
    _unset_primary(db, mapping)
    db.commit()
    db.refresh(mapping)
    return mapping
