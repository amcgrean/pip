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
- Product matching endpoint (`POST /api/v1/products/match`) for OCR-like messy lookup with deterministic scoring across product fields, aliases, and vendor mappings (vendor name/code/SKU first-class, with vendor description/UOM context).
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
See `docs/setup.md` for full instructions and troubleshooting.

### Option A (recommended): Docker Compose
```bash
cp .env.example .env
docker compose up --build -d
docker compose exec backend alembic upgrade head
docker compose exec backend python scripts_seed.py
```

Then open:
- Frontend: `http://localhost:5173`
- API docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/api/v1/health`

### Option B: Run services directly (without Docker)
```bash
cp .env.example .env

# terminal 1 (backend)
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python scripts_seed.py
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# terminal 2 (frontend)
cd frontend
npm ci
npm run dev -- --host 0.0.0.0 --port 5173
```

## Deployment
See `docs/deployment-render.md` for Render-specific steps and required environment variables.

## Known MVP Limitations
- Attachment storage is local filesystem-based (good for MVP/internal usage; not yet cloud object storage).
- No SSO or advanced role model yet.
- No background job queue for large imports.
- Product matching is deterministic/rules-based (no semantic embeddings or ML ranking).

## Deferred (post-launch)
- SSO and stronger IAM model
- Object storage migration (S3/R2/etc.)
- Background workers + retryable asynchronous import pipeline
- External ERP integrations
