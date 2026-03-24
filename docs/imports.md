# Imports

## Endpoints
- `POST /api/v1/imports/products-csv`
  - Backward-compatible entry point for the primary products seed feed.
  - Treated as `products_seed` sheet semantics.
- `POST /api/v1/imports/sheet-csv?sheet_name=<sheet>`
  - Supports workbook-derived CSV exports for:
    - `products_seed`
    - `item_aliases`
    - `item_images`
    - `item_documents`
- `GET /api/v1/imports/jobs`

## Behavior
- Decodes UTF-8 with BOM support (`utf-8-sig`).
- Trims header names and values.
- Validates required columns per sheet.
- Keeps row-level error logging without aborting the full job.
- Uses idempotent upsert logic where appropriate:
  - products upsert by `internal_sku`
  - vendor mappings upsert by `(vendor, product, vendor_sku)`
  - aliases upsert by `(product, alias_text)`
  - images upsert by `(product, storage_path)`
  - documents upsert by `(product, document_type, title)`

## CSV templates

### `products_seed` required columns
- `internal_sku`, `normalized_name`

### `products_seed` recommended columns
- Existing MVP fields:
  - `product_type`, `category_major`, `category_minor`, `species_or_material`, `grade`
  - `thickness`, `width`, `length`, `unit_of_measure`, `description`, `status`, `branch_scope`
- Enrichment fields:
  - `canonical_name`, `display_name`, `extended_description`
  - `category`, `subcategory`, `finish`, `treatment`, `profile`
  - `thickness_numeric`, `width_numeric`, `length_numeric`
  - `keywords`, `search_text`, `master_search_text`
  - `last_sold_date` (format `YYYY-MM-DD`)
  - `is_active`, `is_stock_item`, `match_priority`, `source_system_id`
- Optional seeded note fields:
  - `note_text`, `note_type`
- Optional vendor mapping fields:
  - `vendor_code`, `vendor_name`, `vendor_sku`, `vendor_description`, `vendor_uom`, `last_cost`, `mapping_is_primary`

### `item_aliases` required columns
- `internal_sku`, `alias_text`

### `item_aliases` optional columns
- `alias_type`, `is_preferred`, `source`, `notes`

### `item_images` required columns
- `internal_sku`, `storage_path` (or `image_url`)

### `item_images` optional columns
- `image_type`, `alt_text`, `sort_order`, `source`, `notes`

### `item_documents` required columns
- `internal_sku`, `document_type`, `title`

### `item_documents` optional columns
- `file_url` (or `storage_path`), `effective_date` (format `YYYY-MM-DD`), `source`, `notes`

## Workbook workflow
The importer remains CSV-first for maintainability.

Recommended flow for Excel workbooks:
1. Export each workbook sheet (`products_seed`, `item_aliases`, `item_images`, `item_documents`) to separate CSV files.
2. Import `products_seed` first.
3. Import enrichment sheets in any order after products are loaded.

## Deferred workbook sheets
- `product_relationships`: defer until relationship taxonomy (substitute/upsell/component) is finalized.
- `inventory_by_location`: defer until a stable location master and refresh cadence are defined.
