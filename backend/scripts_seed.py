from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.product import Product
from app.models.product_note import ProductNote
from app.models.user import User
from app.models.vendor import Vendor
from app.models.vendor_product_mapping import VendorProductMapping


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
        db.flush()

    if db.query(Product).count() > 0:
        db.commit()
        return

    vendors = [
        Vendor(vendor_code="UFPI", vendor_name="UFP Industries"),
        Vendor(vendor_code="WYER", vendor_name="Weyerhaeuser"),
        Vendor(vendor_code="TREB", vendor_name="Trex Building Products"),
        Vendor(vendor_code="HUBE", vendor_name="Huber Engineered Woods"),
    ]
    db.add_all(vendors)
    db.flush()

    products = [
        Product(internal_sku="BL-LVL-118-14", normalized_name="LVL Beam 1.75x11.875x14", product_type="Engineered Lumber", category_major="Framing", category_minor="LVL", species_or_material="LVL", unit_of_measure="EA", status="active", description="Structural LVL beam"),
        Product(internal_sku="BL-TRT-2X6-12", normalized_name="Treated Lumber 2x6x12", product_type="Lumber", category_major="Dimensional Lumber", category_minor="Treated", species_or_material="SPF", unit_of_measure="EA", status="active"),
        Product(internal_sku="BL-MDF-1X4-16", normalized_name="MDF Trim Board 1x4x16", product_type="Trim", category_major="Interior Trim", category_minor="MDF", unit_of_measure="EA", status="active"),
        Product(internal_sku="BL-COMP-DECK-12", normalized_name="Composite Deck Board 1x6x12", product_type="Decking", category_major="Decking", category_minor="Composite", unit_of_measure="EA", status="active"),
        Product(internal_sku="BL-ZIP-716-4X8", normalized_name="ZIP Sheathing 7/16 4x8", product_type="Sheet Goods", category_major="Panels", category_minor="ZIP", unit_of_measure="EA", status="active"),
        Product(internal_sku="BL-DOOR-3068", normalized_name="Interior Prehung Door 3-0x6-8", product_type="Door", category_major="Doors", category_minor="Interior", unit_of_measure="EA", status="active"),
        Product(internal_sku="BL-IJOIST-11-20", normalized_name="I-Joist 11-7/8x20", product_type="Engineered Wood", category_major="Framing", category_minor="I-Joist", unit_of_measure="EA", status="active"),
        Product(internal_sku="BL-WIN-3050-DH", normalized_name="Vinyl Double Hung Window 3050", product_type="Window", category_major="Millwork", category_minor="Window", unit_of_measure="EA", status="active"),
    ]
    db.add_all(products)
    db.flush()

    mappings = [
        VendorProductMapping(vendor_id=vendors[0].id, product_id=products[0].id, vendor_sku="UF-LVL-117514", is_primary=True),
        VendorProductMapping(vendor_id=vendors[1].id, product_id=products[4].id, vendor_sku="WY-ZIP-716", is_primary=True),
        VendorProductMapping(vendor_id=vendors[2].id, product_id=products[3].id, vendor_sku="TR-DB-12", is_primary=True),
    ]
    db.add_all(mappings)

    notes = [
        ProductNote(product_id=products[0].id, note_text="Preferred for long-span garage openings.", note_type="ops", created_by=admin.id),
        ProductNote(product_id=products[4].id, note_text="Use Huber tape SKU on same ticket.", note_type="purchasing", created_by=admin.id),
    ]
    db.add_all(notes)
    db.commit()


if __name__ == "__main__":
    session = SessionLocal()
    try:
        seed(session)
        print("Seed complete")
    finally:
        session.close()
