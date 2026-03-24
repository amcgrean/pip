# Beisser Internal Operations Platform

Production-oriented MVP for an internal Product/Vendor workspace.

## Stack
- Backend: FastAPI, SQLAlchemy, Alembic, Pydantic Settings
- Frontend: React + Vite + TypeScript + MUI
- Database: PostgreSQL
- Deployment target: Render (backend web service + frontend static site + managed PostgreSQL)

## Implemented MVP Scope
- JWT login (`/auth/login`) + protected API routes.
- Product list/detail + create/update APIs with server-side filtering/pagination.
- Product search supports case-insensitive matching across SKU, normalized/enriched names, descriptions, keywords, search text, master search text, and alias text.
- Vendor list/create/update APIs.
- Vendor product mappings with single-primary enforcement per product.
- Product notes add/list.
- Product attachments upload/list/download with local storage abstraction.
- CSV imports for product+mapping upserts with import job history and row-level error logs.
- Dashboard summary cards.

## Production Hardening Included
- Environment-driven runtime config with validation for required/safe values.
- Production-safe backend start command (no hot reload by default).
- CORS configured from comma-separated env var (`CORS_ALLOWED_ORIGINS`).
- Request logging middleware, structured validation errors, startup storage checks.
- Health and version endpoints (`/health`, `/version`).
- Attachment upload hardening (extension allowlist, max size, sanitized and unique file names, path-safe download).
- CSV import hardening (max upload size, file type check, blank-row handling, clearer numeric validation errors).
- Frontend API base URL env support, auth-expiry handling, improved loading/submission/error states.

## Quick Start (Local)
See `docs/setup.md` for full instructions.

```bash
cp .env.example .env
docker compose up --build
docker compose exec backend alembic upgrade head
docker compose exec backend python scripts_seed.py
```

## Deployment
See `docs/deployment-render.md` for Render-specific steps and required environment variables.

## Known MVP Limitations
- Attachment storage is local filesystem-based (good for MVP/internal usage; not yet cloud object storage).
- No SSO or advanced role model yet.
- No background job queue for large imports.

## Deferred (post-launch)
- SSO and stronger IAM model
- Object storage migration (S3/R2/etc.)
- Background workers + retryable asynchronous import pipeline
- External ERP integrations
