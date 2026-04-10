"""
scraper_sync.py — Match scraped products to existing stock catalog entries
and attach images. If no match is found, create a new product.

The scraper sends JSON records with:
  supplier, category, product_name, description, image_url, source_url

The matching strategy:
  1. Try exact internal_sku match (scraper-generated SKU)
  2. Try vendor_name + product_name fuzzy match against stock catalog
  3. If no match, create a new product entry
  4. Attach the image URL to the matched/created product
"""

import json
import re
from datetime import datetime, timezone

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.import_job import ImportJob
from app.models.product import Product
from app.models.product_image import ProductImage
from app.models.vendor import Vendor
from app.models.vendor_product_mapping import VendorProductMapping


def _normalize(text: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[\s\-]+", "_", text)
    text = re.sub(r"[^\w]", "", text)
    return text.strip("_") or "unknown"


def _make_scraper_sku(supplier: str, category: str, product_name: str) -> str:
    return f"{_slugify(supplier)}_{_slugify(category)}_{_slugify(product_name)}"[:80]


def _find_vendor_by_supplier(db: Session, supplier_name: str, cache: dict) -> Vendor | None:
    """Find a vendor whose name contains the supplier name (fuzzy)."""
    key = supplier_name.lower()
    if key in cache:
        return cache[key]

    # Try exact match first
    vendor = db.query(Vendor).filter(
        func.lower(Vendor.vendor_name) == key
    ).first()

    if not vendor:
        # Try contains match: "ferche" matches "Ferche Millwork"
        vendor = db.query(Vendor).filter(
            func.lower(Vendor.vendor_name).contains(key)
        ).first()

    if not vendor:
        # Try reverse: "BayerBuilt" matches vendor "Bayer Built Woodworks"
        vendor = db.query(Vendor).filter(
            func.lower(Vendor.vendor_name).contains(key[:5])
        ).first()

    cache[key] = vendor
    return vendor


def _find_stock_match(db: Session, supplier_name: str, product_name: str, vendor: Vendor | None) -> Product | None:
    """Try to find an existing stock product that matches the scraped item.

    Strategy:
    1. If we found the vendor, search products linked to that vendor
       where the description or SKU contains the product name
    2. Search all products where description contains the product name
       AND supplier-related text matches
    """
    norm_name = _normalize(product_name)
    if not norm_name or len(norm_name) < 2:
        return None

    # Strategy 1: Search via vendor mappings
    if vendor:
        # Get all product IDs mapped to this vendor
        mapped_product_ids = (
            db.query(VendorProductMapping.product_id)
            .filter(VendorProductMapping.vendor_id == vendor.id)
            .subquery()
        )

        # Search those products for name match
        match = db.query(Product).filter(
            Product.id.in_(mapped_product_ids),
            Product.is_stock_item.is_(True),
            or_(
                func.lower(Product.normalized_name).contains(norm_name),
                func.lower(Product.internal_sku).contains(norm_name),
                func.lower(Product.description).contains(norm_name),
            ),
        ).first()

        if match:
            return match

        # Try with just the alphanumeric part (e.g., "F202" → "f202")
        alpha_name = re.sub(r"[^a-z0-9]", "", norm_name)
        if alpha_name and len(alpha_name) >= 3:
            match = db.query(Product).filter(
                Product.id.in_(mapped_product_ids),
                Product.is_stock_item.is_(True),
                or_(
                    func.lower(Product.normalized_name).contains(alpha_name),
                    func.lower(Product.internal_sku).contains(alpha_name),
                    func.lower(Product.description).contains(alpha_name),
                ),
            ).first()

            if match:
                return match

    # Strategy 2: Broad search with supplier context
    norm_supplier = _normalize(supplier_name)
    if norm_supplier and norm_name:
        match = db.query(Product).filter(
            Product.is_stock_item.is_(True),
            or_(
                func.lower(Product.species_or_material).contains(norm_supplier),
                func.lower(Product.category_major).contains(norm_supplier),
            ),
            or_(
                func.lower(Product.normalized_name).contains(norm_name),
                func.lower(Product.internal_sku).contains(norm_name),
            ),
        ).first()

        if match:
            return match

    return None


def _attach_image(db: Session, product: Product, image_url: str, product_name: str, source_url: str) -> tuple[int, int]:
    """Attach an image to a product. Returns (inserted, updated)."""
    if not image_url:
        return 0, 0

    existing = db.query(ProductImage).filter(
        ProductImage.product_id == product.id,
        ProductImage.storage_path == image_url,
    ).first()

    if existing:
        existing.source = "pip-scraper"
        return 0, 1

    db.add(ProductImage(
        product_id=product.id,
        storage_path=image_url,
        image_type="product_photo",
        alt_text=product_name[:255] if product_name else None,
        source="pip-scraper",
        notes=f"Scraped from {source_url}" if source_url else None,
    ))
    db.flush()
    return 1, 0


def process_scraper_sync(db: Session, records: list[dict], user_id: int) -> ImportJob:
    """Process scraped product records: match to stock catalog, attach images.

    Each record should have:
      supplier, category, product_name, description, image_url, source_url
    """
    job = ImportJob(
        source_type="scraper_sync",
        file_name="scraper_metadata.json",
        status="processing",
        created_by=user_id,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    vendor_cache: dict = {}
    products_inserted = 0
    products_updated = 0
    images_inserted = 0
    images_updated = 0
    errored = 0
    matched_count = 0
    errors: list[dict] = []

    for idx, rec in enumerate(records):
        try:
            supplier = rec.get("supplier", "")
            category = rec.get("category", "")
            product_name = rec.get("product_name", "")
            description = rec.get("description", "")
            image_url = rec.get("image_url", "")
            source_url = rec.get("source_url", "")

            if not product_name:
                continue

            # Try to find a matching stock product
            vendor = _find_vendor_by_supplier(db, supplier, vendor_cache)
            stock_product = _find_stock_match(db, supplier, product_name, vendor)

            if stock_product:
                # Match found — attach image to existing stock product
                matched_count += 1
                products_updated += 1
                img_ins, img_upd = _attach_image(db, stock_product, image_url, product_name, source_url)
                images_inserted += img_ins
                images_updated += img_upd
            else:
                # No match — create a new product entry from scraper data
                scraper_sku = _make_scraper_sku(supplier, category, product_name)

                existing = db.query(Product).filter(Product.internal_sku == scraper_sku).first()
                if existing:
                    # Update existing scraper-created product
                    existing.description = description or existing.description
                    products_updated += 1
                    product = existing
                else:
                    # Create new
                    product = Product(
                        internal_sku=scraper_sku,
                        normalized_name=product_name[:255],
                        description=description or None,
                        category_major=supplier,
                        category_minor=category,
                        product_type="supplier_image",
                        is_stock_item=False,
                        is_active=True,
                        status="active",
                    )
                    db.add(product)
                    db.flush()
                    products_inserted += 1

                    # Create vendor mapping if we found the vendor
                    if vendor:
                        exists = db.query(VendorProductMapping).filter(
                            VendorProductMapping.vendor_id == vendor.id,
                            VendorProductMapping.product_id == product.id,
                            VendorProductMapping.vendor_sku == scraper_sku,
                        ).first()
                        if not exists:
                            db.add(VendorProductMapping(
                                vendor_id=vendor.id,
                                product_id=product.id,
                                vendor_sku=scraper_sku,
                            ))
                            db.flush()

                # Attach image
                img_ins, img_upd = _attach_image(db, product, image_url, product_name, source_url)
                images_inserted += img_ins
                images_updated += img_upd

        except Exception as exc:  # noqa: BLE001
            errored += 1
            errors.append({"row": str(idx), "error": str(exc)})

    total_rows = products_inserted + products_updated + errored
    job.total_rows = total_rows
    job.inserted_rows = products_inserted
    job.updated_rows = products_updated
    job.error_rows = errored
    job.error_log = json.dumps({
        "matched_to_stock": matched_count,
        "new_products": products_inserted,
        "images_inserted": images_inserted,
        "images_updated": images_updated,
        "errors": errors[:100],
    })
    job.status = "completed_with_errors" if errored else "completed"
    job.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(job)
    return job
