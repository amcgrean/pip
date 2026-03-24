from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.product import Product
from app.models.user import User
from app.models.vendor import Vendor


def seed(db: Session):
    admin = db.query(User).filter(User.email == settings.seed_admin_email).first()
    if not admin:
        admin = User(
            email=settings.seed_admin_email,
            full_name=settings.seed_admin_full_name,
            password_hash=get_password_hash(settings.seed_admin_password),
            role="admin",
            is_active=True,
        )
        db.add(admin)

    if not db.query(Vendor).first():
        db.add_all(
            [
                Vendor(vendor_code="UFPI", vendor_name="UFP Industries"),
                Vendor(vendor_code="WYER", vendor_name="Weyerhaeuser"),
            ]
        )

    if not db.query(Product).first():
        db.add_all(
            [
                Product(
                    internal_sku="BL-2X4-SPF-96",
                    normalized_name="2x4 SPF Stud 96in",
                    product_type="Lumber",
                    category_major="Dimensional Lumber",
                    species_or_material="SPF",
                    grade="Stud",
                    thickness='2"',
                    width='4"',
                    length='96"',
                    unit_of_measure="EA",
                    status="active",
                    branch_scope="ALL",
                ),
                Product(
                    internal_sku="BL-OSB-716-4X8",
                    normalized_name="OSB Sheathing 7/16 4x8",
                    product_type="Sheet Goods",
                    category_major="Panels",
                    species_or_material="OSB",
                    thickness='7/16"',
                    width='48"',
                    length='96"',
                    unit_of_measure="EA",
                    status="active",
                    branch_scope="ALL",
                ),
            ]
        )

    db.commit()


if __name__ == "__main__":
    session = SessionLocal()
    try:
        seed(session)
        print("Seed complete")
    finally:
        session.close()
