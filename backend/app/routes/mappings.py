from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.vendor_product_mapping import VendorProductMapping
from app.utils.deps import get_current_user

router = APIRouter(prefix="/mappings", tags=["mappings"])


@router.get("/")
def list_mappings(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rows = db.query(VendorProductMapping).all()
    return [{"id": row.id, "vendor_id": row.vendor_id, "product_id": row.product_id, "vendor_sku": row.vendor_sku} for row in rows]
