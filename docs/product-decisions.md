# Product Decisions (MVP)

## Key assumptions
- `internal_sku` is the unique product key for upsert.
- Vendor mapping uniqueness is `(vendor_id, product_id, vendor_sku)`.
- One mapping per product can be marked primary; setting one primary unsets others.
- Product note editing/deletion is deferred for MVP.

## Tradeoffs
- Import processing is synchronous for MVP simplicity.
- Row-level errors are stored as JSON text in `import_jobs.error_log` instead of a child table.
- Attachment preview/transcoding is deferred.
- Product list search uses SQL `ILIKE` across multiple product text fields plus alias existence checks; this is simple, debuggable, and works well pre-FTS.

## Product search behavior
- Search input is trimmed; blank/whitespace-only values are treated as "no search filter".
- Search uses case-insensitive OR matching across:
  - `products.internal_sku`
  - `products.normalized_name`
  - `products.description`
  - `products.canonical_name`
  - `products.display_name`
  - `products.keywords`
  - `products.search_text`
  - `products.master_search_text` (catch-all import field)
  - `product_aliases.alias_text` (via `EXISTS`)
- Alias matching is implemented with `EXISTS` semantics (not a broad join) to prevent duplicate product rows and keep pagination/counts correct.

## Product matching behavior
- Matching is intentionally deterministic and rules-based for MVP stability and auditability.
- Matching runs in a service layer and returns explicit `match_reasons` rather than opaque scoring.
- Vendor identity (`vendor_name`, `vendor_code`) and `vendor_sku` are top-tier matching signals.
- Vendor mapping fields (description/UOM) are lower-weight contextual signals used to break ties and improve noisy text lookup.
- Confidence is bucketed from explicit score thresholds:
  - `high` for strongest exact/vendor-aware hits
  - `medium` for meaningful but less exact text overlap
  - `low` for weak partial/token-only hits
- No ML/LLM/embeddings are used in MVP matching.

## Matching limitations (current)
- Substring and token-overlap heuristics may still miss heavily abbreviated/typo-heavy text.
- No cross-line OCR context yet (line-level reconciliation workflows are future work).
- No learning-to-rank feedback loop; scoring weights are static and code-configured.

## Why this supports future modules
The same patterns can be reused for request/bid tools, warehouse utility modules, and review workflows that need:
- operational list/detail pages
- upload + parse + reconcile flows
- lightweight audit history

## Future data domains (deferred)
- `product_relationships`: add a typed bridge table once relationship types and business rules are finalized.
- `inventory_by_location`: add once location master/source-of-truth and sync expectations are settled.
