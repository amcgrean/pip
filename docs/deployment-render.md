# Render Deployment Guide (First Production Deploy)

This runbook is for first deploy of this internal MVP on Render with managed PostgreSQL.

- Backend: Render Web Service (`backend/`)
- Frontend: Render Static Site (`frontend/`)
- Database: Render PostgreSQL
- Blueprint: `render.yaml` at repo root

## Deployment strategy (recommended)

For this first deploy, keep migrations **automatic per deploy** via Render `releaseCommand`:

- `releaseCommand: alembic upgrade head`
- `startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Why this is the current recommendation:
- It guarantees each deploy uses the latest schema before app startup.
- It removes a fragile manual step during operator handoff.
- If migration fails, deploy fails clearly before serving traffic.

If a future migration is risky/long-running, temporarily switch to manual migration for that release and document it in the release notes.

---

## 1) Create Render PostgreSQL

1. In Render, create PostgreSQL instance named `beisser-ops-db` (or update `render.yaml` names consistently).
2. Keep credentials managed by Render.
3. Confirm DB is available before backend deploy.

---

## 2) Create backend service

1. Create web service from this repo.
2. Confirm:
   - Root Directory: `backend`
   - Build command: `pip install -r requirements.txt`
   - Release command: `alembic upgrade head`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Health check path: `/api/v1/health`
3. Attach `DATABASE_URL` from Render Postgres connection string.

### Required backend environment variables

- `ENVIRONMENT=production`
- `DEBUG=false`
- `LOG_LEVEL=INFO`
- `API_V1_PREFIX=/api/v1`
- `APP_VERSION=<git-sha-or-release-tag>`
- `DATABASE_URL=<from Render PostgreSQL>`
- `SECRET_KEY=<long random value, minimum 16 chars>`
- `ACCESS_TOKEN_EXPIRE_MINUTES=480` (or your policy)
- `ALGORITHM=HS256`
- `CORS_ALLOWED_ORIGINS=https://<frontend-domain>`
- `LOCAL_STORAGE_DIR=/opt/render/project/src/backend/data_storage`
- `MAX_ATTACHMENT_SIZE_BYTES=10485760`
- `MAX_IMPORT_SIZE_BYTES=5242880`
- `ALLOWED_ATTACHMENT_EXTENSIONS=.pdf,.png,.jpg,.jpeg,.csv,.txt,.doc,.docx,.xlsx`

Optional for first seed only:
- `SEED_ADMIN_EMAIL`
- `SEED_ADMIN_PASSWORD`
- `SEED_ADMIN_FULL_NAME`

> Production safety checks are enforced at startup: app refuses to boot with placeholder `SECRET_KEY` or local/dev DB URL.

---

## 3) Create frontend static site

1. Create static site from this repo.
2. Confirm:
   - Root Directory: `frontend`
   - Build command: `npm ci && npm run build`
   - Publish directory: `dist`
3. Set:
   - `VITE_API_BASE_URL=https://<backend-domain>/api/v1`
4. Redeploy frontend after setting env var (Vite injects at build time).

`render.yaml` includes SPA rewrite to `index.html` so deep links work.

---

## 4) First deploy run order

1. Deploy database.
2. Deploy backend (release command runs migrations).
3. Seed admin from backend shell once:
   ```bash
   python scripts_seed.py
   ```
4. Deploy frontend (or trigger manual redeploy after `VITE_API_BASE_URL` is set).

---

## 5) Post-deploy verification checklist

Run these in order:

1. **Verify backend health**
   - `GET https://<backend>/api/v1/health/live` (liveness)
   - `GET https://<backend>/api/v1/health` (DB readiness)
2. **Verify backend version**
   - `GET https://<backend>/api/v1/version`
   - Ensure `version` and `environment` values are expected.
3. **Verify login**
   - Sign in using seeded admin credentials.
4. **Verify product list API**
   - `GET /api/v1/products/` from UI after login.
5. **Verify import endpoints**
   - `POST /api/v1/imports/products-csv` pilot CSV.
6. **Verify deterministic matching endpoint with real sample**
   - `POST /api/v1/products/match` with vendor-aware payload (vendor code/name/SKU + query).

---

## 6) Migration operations after first deploy

Default steady-state:
- Keep `releaseCommand` for migrations.
- Every deploy automatically runs `alembic upgrade head`.

Operational caveats:
- If release command fails, deploy fails before traffic cutover.
- For unusual/high-risk migrations, run manually first from Render shell:
  ```bash
  alembic upgrade head
  ```
  Then deploy app code.

---

## 7) Storage behavior on Render (MVP)

Current behavior is local filesystem storage for attachments.

- Path defaults to `LOCAL_STORAGE_DIR=/opt/render/project/src/backend/data_storage`.
- This is acceptable for internal MVP trials.
- **Limitation:** files are not durable across instance replacement/redeploy events unless persistent disk/object storage is used.

Do not treat attachments as durable records yet. Keep source files in system-of-record storage until object storage migration is implemented.

---

## 8) Failure diagnostics

If deploy fails:

1. Check Render deploy logs for `releaseCommand` migration output.
2. Check backend startup logs for `startup_db_connectivity_failed`.
3. Verify `DATABASE_URL`, `SECRET_KEY`, and `CORS_ALLOWED_ORIGINS` values.
4. If frontend cannot call backend:
   - Verify frontend `VITE_API_BASE_URL` value
   - Verify backend CORS origin exactly matches frontend scheme + host.

---

## Known MVP limitations

- Attachment storage is local filesystem (non-durable on service replacement).
- No background workers for large imports.
- No SSO / advanced RBAC yet.
- Matching is deterministic rules-based (not semantic/ML ranking).
