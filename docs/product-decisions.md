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

## Why this supports future modules
The same patterns can be reused for request/bid tools, warehouse utility modules, and review workflows that need:
- operational list/detail pages
- upload + parse + reconcile flows
- lightweight audit history
