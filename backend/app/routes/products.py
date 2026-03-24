from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.product import Product
from app.models.user import User
from app.schemas.domain import ProductOut
from app.utils.deps import get_current_user

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Product).order_by(Product.normalized_name.asc()).all()
