from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.vendor import Vendor
from app.schemas.domain import VendorCreate, VendorOut, VendorUpdate
from app.services import vendors as vendor_service
from app.utils.deps import get_current_user

router = APIRouter(prefix="/vendors", tags=["vendors"])


@router.get("/", response_model=list[VendorOut])
def list_vendors(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return vendor_service.list_vendors(db)


@router.post("/", response_model=VendorOut, status_code=status.HTTP_201_CREATED)
def create_vendor(payload: VendorCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return vendor_service.create_vendor(db, payload)


@router.put("/{vendor_id}", response_model=VendorOut)
def update_vendor(vendor_id: int, payload: VendorUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor_service.update_vendor(db, vendor, payload)
