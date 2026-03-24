import csv
import io
import json
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.import_job import ImportJob
from app.models.product import Product
from app.models.vendor import Vendor
from app.models.vendor_product_mapping import VendorProductMapping

REQUIRED_COLUMNS = {"internal_sku", "normalized_name", "vendor_code", "vendor_sku"}


def list_jobs(db: Session, page: int, page_size: int):
    query = db.query(ImportJob).order_by(ImportJob.created_at.desc())
    total = query.count()
    rows = query.offset((page - 1) * page_size).limit(page_size).all()
    return rows, total


def _clean_row(row: dict[str, str]) -> dict[str, str]:
    clean = {}
    for key, value in row.items():
        clean[(key or "").strip()] = (value or "").strip()
    return clean


def process_product_csv_import(db: Session, file_name: str, content: bytes, user_id: int):
    job = ImportJob(source_type="product_csv", file_name=file_name, status="processing", created_by=user_id)
    db.add(job)
    db.commit()
    db.refresh(job)

    text = content.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        job.status = "failed"
        job.error_log = "CSV is missing headers"
        db.commit()
        return job

    headers = {h.strip() for h in reader.fieldnames}
    missing = REQUIRED_COLUMNS - headers
    if missing:
        job.status = "failed"
        job.error_log = f"Missing required columns: {', '.join(sorted(missing))}"
        db.commit()
        return job

    inserted = 0
    updated = 0
    errored = 0
    errors: list[dict[str, str]] = []

    for index, raw_row in enumerate(reader, start=2):
        row = _clean_row(raw_row)
        job.total_rows += 1
        try:
            sku = row.get("internal_sku", "")
            name = row.get("normalized_name", "")
            vendor_code = row.get("vendor_code", "")
            vendor_sku = row.get("vendor_sku", "")
            if not all([sku, name, vendor_code, vendor_sku]):
                raise ValueError("required values missing")

            product = db.query(Product).filter(Product.internal_sku == sku).first()
            product_values = {
                "normalized_name": name,
                "product_type": row.get("product_type") or None,
                "category_major": row.get("category_major") or None,
                "category_minor": row.get("category_minor") or None,
                "species_or_material": row.get("species_or_material") or None,
                "grade": row.get("grade") or None,
                "thickness": row.get("thickness") or None,
                "width": row.get("width") or None,
                "length": row.get("length") or None,
                "unit_of_measure": row.get("unit_of_measure") or None,
                "description": row.get("description") or None,
                "status": row.get("status") or "active",
            }
            if product:
                for key, value in product_values.items():
                    setattr(product, key, value)
                updated += 1
            else:
                product = Product(internal_sku=sku, **product_values)
                db.add(product)
                db.flush()
                inserted += 1

            vendor = db.query(Vendor).filter(Vendor.vendor_code == vendor_code).first()
            if not vendor:
                vendor = Vendor(vendor_code=vendor_code, vendor_name=vendor_code, is_active=True)
                db.add(vendor)
                db.flush()

            mapping = (
                db.query(VendorProductMapping)
                .filter(
                    VendorProductMapping.vendor_id == vendor.id,
                    VendorProductMapping.product_id == product.id,
                    VendorProductMapping.vendor_sku == vendor_sku,
                )
                .first()
            )
            mapping_values = {
                "vendor_description": row.get("vendor_description") or None,
                "vendor_uom": row.get("vendor_uom") or None,
                "last_cost": Decimal(row["last_cost"]) if row.get("last_cost") else None,
            }
            if mapping:
                for key, value in mapping_values.items():
                    setattr(mapping, key, value)
            else:
                db.add(
                    VendorProductMapping(
                        vendor_id=vendor.id,
                        product_id=product.id,
                        vendor_sku=vendor_sku,
                        **mapping_values,
                    )
                )
        except Exception as exc:  # noqa: BLE001
            errored += 1
            errors.append({"row": str(index), "error": str(exc)})

    job.inserted_rows = inserted
    job.updated_rows = updated
    job.error_rows = errored
    job.error_log = json.dumps(errors[:100]) if errors else None
    job.status = "completed_with_errors" if errored else "completed"
    job.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(job)
    return job
