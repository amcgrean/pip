import csv
import io
import json
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.import_job import ImportJob
from app.models.product import Product
from app.models.product_alias import ProductAlias
from app.models.product_document import ProductDocument
from app.models.product_image import ProductImage
from app.models.product_note import ProductNote
from app.models.vendor import Vendor
from app.models.vendor_product_mapping import VendorProductMapping

REQUIRED_COLUMNS = {
    "products_seed": {"internal_sku", "normalized_name"},
    "item_aliases": {"internal_sku", "alias_text"},
    "item_images": {"internal_sku", "storage_path"},
    "item_documents": {"internal_sku", "document_type", "title"},
}


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


def _is_blank_row(row: dict[str, str]) -> bool:
    return not any(value.strip() for value in row.values())


def _parse_decimal(value: str | None, field_name: str) -> Decimal | None:
    if not value:
        return None
    try:
        return Decimal(value)
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"Invalid {field_name} value: {value}") from exc


def _parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None or value == "":
        return default
    normalized = value.strip().lower()
    return normalized in {"1", "true", "yes", "y"}


def _parse_float(value: str | None, field_name: str) -> float | None:
    if not value:
        return None
    try:
        return float(value)
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"Invalid {field_name} value: {value}") from exc


def _parse_int(value: str | None, field_name: str) -> int | None:
    if not value:
        return None
    try:
        return int(value)
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"Invalid {field_name} value: {value}") from exc


def _parse_date(value: str | None, field_name: str) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError(f"Invalid {field_name} date (expected YYYY-MM-DD): {value}") from exc


def _resolve_product(db: Session, row: dict[str, str]) -> Product:
    sku = row.get("internal_sku", "")
    if not sku:
        raise ValueError("internal_sku is required")
    product = db.query(Product).filter(Product.internal_sku == sku).first()
    if not product:
        raise ValueError(f"Product not found for internal_sku={sku}")
    return product


def _upsert_vendor_mapping(db: Session, product: Product, row: dict[str, str]) -> tuple[int, int]:
    vendor_code = row.get("vendor_code") or ""
    vendor_sku = row.get("vendor_sku") or ""
    if not vendor_code or not vendor_sku:
        return 0, 0

    vendor = db.query(Vendor).filter(Vendor.vendor_code == vendor_code).first()
    if not vendor:
        vendor = Vendor(vendor_code=vendor_code, vendor_name=row.get("vendor_name") or vendor_code, is_active=True)
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
        "last_cost": _parse_decimal(row.get("last_cost"), "last_cost"),
        "is_primary": _parse_bool(row.get("mapping_is_primary"), default=False),
    }
    if mapping_values["is_primary"]:
        db.query(VendorProductMapping).filter(
            VendorProductMapping.product_id == product.id,
            VendorProductMapping.is_primary.is_(True),
            VendorProductMapping.id != (mapping.id if mapping else 0),
        ).update({"is_primary": False}, synchronize_session=False)

    if mapping:
        for key, value in mapping_values.items():
            setattr(mapping, key, value)
        return 0, 1

    db.add(
        VendorProductMapping(
            vendor_id=vendor.id,
            product_id=product.id,
            vendor_sku=vendor_sku,
            **mapping_values,
        )
    )
    return 1, 0


def _upsert_product_note(db: Session, product: Product, row: dict[str, str], user_id: int):
    note_text = row.get("note_text") or ""
    if not note_text:
        return

    note_type = row.get("note_type") or "seed"
    existing = (
        db.query(ProductNote)
        .filter(ProductNote.product_id == product.id, ProductNote.note_type == note_type, ProductNote.note_text == note_text)
        .first()
    )
    if not existing:
        db.add(ProductNote(product_id=product.id, note_text=note_text, note_type=note_type, created_by=user_id))


def _process_products_seed_row(db: Session, row: dict[str, str], user_id: int) -> tuple[int, int]:
    sku = row.get("internal_sku", "")
    name = row.get("normalized_name", "")
    if not sku or not name:
        raise ValueError("required values missing: internal_sku, normalized_name")

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
        "branch_scope": row.get("branch_scope") or None,
        "canonical_name": row.get("canonical_name") or None,
        "display_name": row.get("display_name") or None,
        "extended_description": row.get("extended_description") or None,
        "category": row.get("category") or None,
        "subcategory": row.get("subcategory") or None,
        "finish": row.get("finish") or None,
        "treatment": row.get("treatment") or None,
        "profile": row.get("profile") or None,
        "thickness_numeric": _parse_float(row.get("thickness_numeric"), "thickness_numeric"),
        "width_numeric": _parse_float(row.get("width_numeric"), "width_numeric"),
        "length_numeric": _parse_float(row.get("length_numeric"), "length_numeric"),
        "keywords": row.get("keywords") or None,
        "search_text": row.get("search_text") or None,
        "master_search_text": row.get("master_search_text") or None,
        "last_sold_date": _parse_date(row.get("last_sold_date"), "last_sold_date"),
        "is_active": _parse_bool(row.get("is_active"), default=(row.get("status", "active") != "inactive")),
        "is_stock_item": _parse_bool(row.get("is_stock_item"), default=False),
        "match_priority": _parse_int(row.get("match_priority"), "match_priority"),
        "source_system_id": row.get("source_system_id") or None,
    }

    if product:
        for key, value in product_values.items():
            setattr(product, key, value)
        inserted, updated = 0, 1
    else:
        product = Product(internal_sku=sku, **product_values)
        db.add(product)
        db.flush()
        inserted, updated = 1, 0

    _upsert_product_note(db, product, row, user_id)
    _upsert_vendor_mapping(db, product, row)
    return inserted, updated


def _process_alias_row(db: Session, row: dict[str, str]) -> tuple[int, int]:
    product = _resolve_product(db, row)
    alias_text = row.get("alias_text") or ""
    if not alias_text:
        raise ValueError("alias_text is required")

    alias = db.query(ProductAlias).filter(ProductAlias.product_id == product.id, ProductAlias.alias_text == alias_text).first()
    values = {
        "alias_type": row.get("alias_type") or None,
        "is_preferred": _parse_bool(row.get("is_preferred"), default=False),
        "source": row.get("source") or None,
        "notes": row.get("notes") or None,
    }
    if alias:
        for key, value in values.items():
            setattr(alias, key, value)
        return 0, 1

    db.add(ProductAlias(product_id=product.id, alias_text=alias_text, **values))
    return 1, 0


def _process_image_row(db: Session, row: dict[str, str]) -> tuple[int, int]:
    product = _resolve_product(db, row)
    storage_path = row.get("storage_path") or row.get("image_url") or ""
    if not storage_path:
        raise ValueError("storage_path (or image_url) is required")

    image = db.query(ProductImage).filter(ProductImage.product_id == product.id, ProductImage.storage_path == storage_path).first()
    values = {
        "image_type": row.get("image_type") or None,
        "alt_text": row.get("alt_text") or None,
        "sort_order": _parse_int(row.get("sort_order"), "sort_order") or 0,
        "source": row.get("source") or None,
        "notes": row.get("notes") or None,
    }
    if image:
        for key, value in values.items():
            setattr(image, key, value)
        return 0, 1

    db.add(ProductImage(product_id=product.id, storage_path=storage_path, **values))
    return 1, 0


def _process_document_row(db: Session, row: dict[str, str]) -> tuple[int, int]:
    product = _resolve_product(db, row)
    document_type = row.get("document_type") or ""
    title = row.get("title") or ""
    if not document_type or not title:
        raise ValueError("document_type and title are required")

    record = (
        db.query(ProductDocument)
        .filter(ProductDocument.product_id == product.id, ProductDocument.document_type == document_type, ProductDocument.title == title)
        .first()
    )
    values = {
        "file_url": row.get("file_url") or row.get("storage_path") or None,
        "source": row.get("source") or None,
        "effective_date": _parse_date(row.get("effective_date"), "effective_date"),
        "notes": row.get("notes") or None,
    }
    if record:
        for key, value in values.items():
            setattr(record, key, value)
        return 0, 1

    db.add(ProductDocument(product_id=product.id, document_type=document_type, title=title, **values))
    return 1, 0


def _process_csv_import(db: Session, file_name: str, content: bytes, user_id: int, source_type: str):
    job = ImportJob(source_type=source_type, file_name=file_name, status="processing", created_by=user_id)
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
    missing = REQUIRED_COLUMNS[source_type] - headers
    if missing:
        job.status = "failed"
        job.error_log = f"Missing required columns: {', '.join(sorted(missing))}"
        db.commit()
        return job

    inserted = 0
    updated = 0
    errored = 0
    errors: list[dict[str, str]] = []

    processors = {
        "products_seed": lambda row: _process_products_seed_row(db, row, user_id),
        "item_aliases": lambda row: _process_alias_row(db, row),
        "item_images": lambda row: _process_image_row(db, row),
        "item_documents": lambda row: _process_document_row(db, row),
    }

    for index, raw_row in enumerate(reader, start=2):
        row = _clean_row(raw_row)
        if _is_blank_row(row):
            continue
        job.total_rows += 1
        try:
            row_inserted, row_updated = processors[source_type](row)
            inserted += row_inserted
            updated += row_updated
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


def process_product_csv_import(db: Session, file_name: str, content: bytes, user_id: int):
    return _process_csv_import(db, file_name, content, user_id, source_type="products_seed")


def process_sheet_csv_import(db: Session, file_name: str, content: bytes, user_id: int, sheet_name: str):
    if sheet_name not in REQUIRED_COLUMNS:
        raise ValueError(f"Unsupported sheet_name '{sheet_name}'")
    return _process_csv_import(db, file_name, content, user_id, source_type=sheet_name)
