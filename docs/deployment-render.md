# Render Deployment Guide

This document describes the recommended initial deployment for this internal MVP:
- Backend: Render Web Service (Python)
- Frontend: Render Static Site
- Database: Render PostgreSQL

A baseline `render.yaml` is included at repo root.

## 1) Create Render resources
1. Create PostgreSQL instance.
2. Create backend web service from this repo (`rootDir: backend`).
3. Create frontend static site from this repo (`rootDir: frontend`).

## 2) Backend settings
### Build/start
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Required environment variables
- `ENVIRONMENT=production`
- `DEBUG=false`
- `LOG_LEVEL=INFO`
- `API_V1_PREFIX=/api/v1`
- `APP_VERSION` (set to release tag or commit)
- `DATABASE_URL` (from Render Postgres connection string)
- `SECRET_KEY` (long random value)
- `ACCESS_TOKEN_EXPIRE_MINUTES=480` (or preferred)
- `CORS_ALLOWED_ORIGINS=https://<your-frontend-domain>`
- `LOCAL_STORAGE_DIR=/opt/render/project/src/backend/data_storage`
- `MAX_ATTACHMENT_SIZE_BYTES=10485760`
- `MAX_IMPORT_SIZE_BYTES=5242880`
- `ALLOWED_ATTACHMENT_EXTENSIONS=.pdf,.png,.jpg,.jpeg,.csv,.txt,.doc,.docx,.xlsx`
- `SEED_ADMIN_EMAIL` (required only for first-time seed run)
- `SEED_ADMIN_PASSWORD` (required only for first-time seed run)
- `SEED_ADMIN_FULL_NAME` (optional; defaults to Internal Admin)

## 3) Frontend settings
### Build/publish
- Build command: `npm ci && npm run build`
- Publish directory: `dist`

### Required environment variable
- `VITE_API_BASE_URL=https://<your-backend-domain>/api/v1`

## 4) Database migration and seeding
After first backend deploy, run once from a Render shell:
```bash
alembic upgrade head
python scripts_seed.py
```

If you prefer no shell access, run the same two commands in a one-off Render job tied to the backend service.

## 5) Smoke checks
- `GET /api/v1/health` returns `status: ok`
- `GET /api/v1/version` returns expected app version/environment
- Frontend login succeeds
- Product list page loads
- CSV import + attachment upload work within configured limits

## Known limitations for this deployment shape
- Attachment files are stored on local service disk; this is suitable for MVP only.
- If backend service is redeployed/moved, files may be lost unless persistent disk is configured.
- Recommended next step after launch: migrate attachment storage to object storage.

## Post-launch recommended next steps
1. Add persistent disk or object storage for attachments.
2. Add CI test/build pipeline gates.
3. Add periodic DB backup verification and restore drill.
4. Add SSO and stronger role-based access control.
