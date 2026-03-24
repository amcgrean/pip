# Imports and Initial Data Load Runbook

## Endpoints
- `POST /api/v1/imports/products-csv`
  - Primary seed feed (`products_seed` semantics).
- `POST /api/v1/imports/sheet-csv?sheet_name=<sheet>`
  - Supports: `products_seed`, `item_aliases`, `item_images`, `item_documents`.
- `GET /api/v1/imports/jobs`
  - Import history + row-level error logs.

## Import behavior
- UTF-8 with BOM support (`utf-8-sig`).
- Header/value trimming.
- Required-column validation per sheet.
- Row-level error logging without aborting full job.
- Idempotent upsert behavior:
  - products by `internal_sku`
  - vendor mappings by `(vendor, product, vendor_sku)`
  - aliases by `(product, alias_text)`
  - images by `(product, storage_path)`
  - documents by `(product, document_type, title)`

---

## First real product load: recommended sequence

Use this sequence for first production data load:

1. **Pilot `products_seed` import** (10–50 rows, mixed vendors).
2. Validate product list/search + product detail pages.
3. Validate `/api/v1/products/match` against known vendor SKUs/descriptions.
4. Import `item_aliases` pilot rows.
5. Re-check search and matcher lift from aliases.
6. Import `item_images` and `item_documents` pilot rows.
7. If all checks pass, run full imports in the same order.

### Why this order
- Products establish canonical keys (`internal_sku`) for all enrichment sheets.
- Aliases strongly affect search/matching quality and should be verified early.
- Images/documents are lower risk and can trail core matching data.

---

## Required vs critical fields

### `products_seed` required columns
- `internal_sku`
- `normalized_name`

### Matching/search-critical fields (highest ROI)
For first deploy quality, prioritize completeness/accuracy of:
- `internal_sku`
- `vendor_code`
- `vendor_name`
- `vendor_sku`
- `vendor_description`
- `vendor_uom`
- `aliases` (`item_aliases.alias_text`)
- `search_text`
- `master_search_text`

### Strongly recommended `products_seed` columns
- Existing fields:
  - `product_type`, `category_major`, `category_minor`, `species_or_material`, `grade`
  - `thickness`, `width`, `length`, `unit_of_measure`, `description`, `status`, `branch_scope`
- Enrichment:
  - `canonical_name`, `display_name`, `extended_description`
  - `category`, `subcategory`, `finish`, `treatment`, `profile`
  - `thickness_numeric`, `width_numeric`, `length_numeric`
  - `keywords`, `search_text`, `master_search_text`
  - `last_sold_date` (`YYYY-MM-DD`)
  - `is_active`, `is_stock_item`, `match_priority`, `source_system_id`
- Optional seed note fields:
  - `note_text`, `note_type`
- Optional mapping fields:
  - `vendor_code`, `vendor_name`, `vendor_sku`, `vendor_description`, `vendor_uom`, `last_cost`, `mapping_is_primary`

---

## Supplemental sheets

### `item_aliases`
Required:
- `internal_sku`, `alias_text`

Optional:
- `alias_type`, `is_preferred`, `source`, `notes`

### `item_images`
Required:
- `internal_sku`, `storage_path` (or `image_url`)

Optional:
- `image_type`, `alt_text`, `sort_order`, `source`, `notes`

### `item_documents`
Required:
- `internal_sku`, `document_type`, `title`

Optional:
- `file_url` (or `storage_path`), `effective_date` (`YYYY-MM-DD`), `source`, `notes`

---

## Common data mistakes to avoid

1. Inconsistent vendor identity (`vendor_code`/`vendor_name` drift for same vendor).
2. Reused `vendor_sku` values with incorrect vendor pairing.
3. Missing `vendor_sku` on rows where mapping is expected.
4. Overly sparse `search_text` / `master_search_text`.
5. Alias rows pointing to unknown `internal_sku`.
6. Bad numeric/date formatting (`last_cost`, `last_sold_date`).
7. Marking multiple mappings as primary for one product in a single load batch.

---

## Pilot import checklist (before full load)

Use a small pilot CSV and confirm:

1. `GET /api/v1/imports/jobs` shows status `completed`.
2. Error rows are zero or understood/acceptable.
3. Product search finds pilot SKUs and keyword phrases.
4. Product detail contains expected mappings/aliases/notes.
5. `/api/v1/products/match` returns expected top result for:
   - exact vendor SKU
   - vendor-aware lookup (`vendor_code`/`vendor_name`)
   - noisy query text with SKU/description hints

---

## Workbook workflow

Importer remains CSV-first.

Recommended workbook flow:
1. Export workbook sheets to CSV (`products_seed`, `item_aliases`, `item_images`, `item_documents`).
2. Import `products_seed` first.
3. Import remaining sheets after product keys exist.

## Deferred workbook sheets
- `product_relationships` (deferred pending taxonomy finalization).
- `inventory_by_location` (deferred pending stable location model + cadence).
