from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.import_job import ImportJob
from app.models.product import Product
from app.models.product_attachment import ProductAttachment
from app.models.vendor import Vendor


def get_summary(db: Session):
    total_active_products = db.query(func.count(Product.id)).filter(Product.status == "active").scalar() or 0
    total_vendors = db.query(func.count(Vendor.id)).scalar() or 0
    products_with_attachments = (
        db.query(func.count(func.distinct(ProductAttachment.product_id))).scalar() or 0
    )
    recent_import_jobs = db.query(ImportJob).order_by(ImportJob.created_at.desc()).limit(5).all()
    return {
        "total_active_products": total_active_products,
        "total_vendors": total_vendors,
        "products_with_attachments": products_with_attachments,
        "recent_import_jobs": recent_import_jobs,
    }
