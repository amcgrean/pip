# Architecture Overview

## Module boundaries
- `backend/app/routes/*`: HTTP transport + request/response shaping.
- `backend/app/services/*`: domain logic and workflow orchestration.
- `backend/app/models/*`: SQLAlchemy entities.
- `backend/app/schemas/*`: API contracts.
- `frontend/src/pages/*`: feature screens.
- `frontend/src/api/client.ts`: centralized API client + auth/session interception.

## Request flow
1. Request enters FastAPI route.
2. Route resolves auth (`get_current_user`) and DB session dependency.
3. Service layer performs business logic.
4. Route returns typed response schema.

## Product list search/query behavior
- Product list queries are built in the service layer with composable SQLAlchemy filters (search + vendor/category/status/attachment filters).
- Search is case-insensitive (`ILIKE`) and OR-based across core + enriched product text fields.
- Alias matching uses an `EXISTS` subquery (`Product.aliases.any(...)`) so alias hits do not duplicate product rows.
- Pagination/count behavior remains stable by deduplicating at the product level before paging.

## Product matching behavior (`POST /api/v1/products/match`)
- Implemented as a two-stage backend matcher in `app/services/product_matching.py`:
  1. Candidate retrieval using SQL filters over product text fields, aliases, vendor mappings, and vendor identity inputs.
  2. Deterministic Python scoring with explicit weights and explainable reasons.
- Primary matching inputs:
  - `query_text` (messy OCR-style text, SKU fragments, descriptions)
  - optional `vendor_name`
  - optional `vendor_code`
  - optional `vendor_sku`
- Vendor signals are first-class:
  - exact `vendor_sku` matches are one of the highest-weight rules
  - vendor name/code alignment boosts mapping-linked products
  - vendor UOM can provide a light relevance signal for ambiguous text
  - best matching vendor mapping metadata is returned with the result
- Match responses include:
  - product identity/display fields
  - numeric score
  - confidence bucket (`high`/`medium`/`low`)
  - `match_reasons` explanation list
  - matched vendor mapping context (when present)

## Configuration model
- All runtime settings are environment-driven (`backend/app/core/config.py`).
- Settings include validation (environment, log level, secret length, file-size limits).
- CORS is configured through `CORS_ALLOWED_ORIGINS` (comma-separated).

## Storage design (attachments)
- Current storage provider: local filesystem (`LocalStorageService`).
- Stored file names are sanitized and uniquified.
- DB stores a relative path; download resolution enforces root-bound path safety.
- This provider is intentionally simple to support a future object-storage swap.

## Import design
- CSV imports are synchronous MVP workflows.
- Required header validation, per-row parse/validation, row-level error capture.
- Blank rows are skipped.
- Import job table tracks totals, status, and error snippets.

## Operational endpoints
- `GET /api/v1/health`: app + DB connectivity status.
- `GET /api/v1/version`: build/version metadata.
