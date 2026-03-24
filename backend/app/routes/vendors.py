from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.vendor import Vendor
from app.schemas.domain import VendorOut
from app.utils.deps import get_current_user

router = APIRouter(prefix="/vendors", tags=["vendors"])


@router.get("/", response_model=list[VendorOut])
def list_vendors(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Vendor).order_by(Vendor.vendor_name.asc()).all()
