# Imports

## Endpoint
- `POST /api/v1/imports/products-csv`
- `GET /api/v1/imports/jobs`

## Behavior
- Decodes UTF-8 with BOM support (`utf-8-sig`).
- Trims header names and values.
- Validates required columns.
- Upserts products by `internal_sku`.
- Upserts mappings by `(vendor, product, vendor_sku)`.
- Captures row-level errors without aborting entire job.

## CSV template
Recommended columns:
- `internal_sku`, `normalized_name`, `product_type`, `category_major`, `category_minor`
- `species_or_material`, `grade`, `thickness`, `width`, `length`
- `unit_of_measure`, `description`, `status`
- `vendor_code`, `vendor_sku`, `vendor_description`, `vendor_uom`, `last_cost`
