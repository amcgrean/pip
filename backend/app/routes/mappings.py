from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.vendor_product_mapping import VendorProductMapping
from app.schemas.domain import VendorMappingCreate, VendorMappingOut, VendorMappingUpdate
from app.services import mappings as mapping_service
from app.utils.deps import get_current_user

router = APIRouter(prefix="/mappings", tags=["mappings"])


@router.get("/product/{product_id}", response_model=list[VendorMappingOut])
def list_mappings(product_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rows = mapping_service.list_for_product(db, product_id)
    return [
        {
            **row.__dict__,
            "vendor_name": row.vendor.vendor_name if row.vendor else None,
            "vendor_code": row.vendor.vendor_code if row.vendor else None,
        }
        for row in rows
    ]


@router.post("/", response_model=VendorMappingOut, status_code=status.HTTP_201_CREATED)
def create_mapping(payload: VendorMappingCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return mapping_service.create_mapping(db, payload)


@router.put("/{mapping_id}", response_model=VendorMappingOut)
def update_mapping(mapping_id: int, payload: VendorMappingUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    mapping = db.query(VendorProductMapping).filter(VendorProductMapping.id == mapping_id).first()
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")
    return mapping_service.update_mapping(db, mapping, payload)
