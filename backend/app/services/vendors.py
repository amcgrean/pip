from sqlalchemy import asc
from sqlalchemy.orm import Session

from app.models.vendor import Vendor
from app.schemas.domain import VendorCreate, VendorUpdate


def list_vendors(db: Session):
    return db.query(Vendor).order_by(asc(Vendor.vendor_name)).all()


def create_vendor(db: Session, payload: VendorCreate):
    vendor = Vendor(**payload.model_dump())
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor


def update_vendor(db: Session, vendor: Vendor, payload: VendorUpdate):
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(vendor, key, value)
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor
