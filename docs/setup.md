# Setup & Operations Guide

## Prerequisites
- Docker Desktop (or Docker Engine + Compose plugin)
- GNU Make (optional, if using Makefile helpers)

## Local setup
1. Copy environment template:
   ```bash
   cp .env.example .env
   ```
2. Build and start the stack:
   ```bash
   docker compose up --build
   ```
3. Run database migrations:
   ```bash
   docker compose exec backend alembic upgrade head
   ```
4. Seed admin/demo data:
   ```bash
   docker compose exec backend python scripts_seed.py
   ```
5. Open the UI: `http://localhost:5173`

## Runtime URLs
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000/api/v1`
- Health: `http://localhost:8000/api/v1/health`
- Version: `http://localhost:8000/api/v1/version`

## Fresh DB reset
```bash
docker compose down -v
docker compose up --build -d
docker compose exec backend alembic upgrade head
docker compose exec backend python scripts_seed.py
```

## Common commands
- Start/restart:
  ```bash
  docker compose up --build
  ```
- Stop:
  ```bash
  docker compose down
  ```
- Logs:
  ```bash
  docker compose logs -f backend frontend db
  ```
- Run backend tests:
  ```bash
  cd backend && pytest
  ```
- Build frontend:
  ```bash
  cd frontend && npm ci && npm run build
  ```

## Important configuration variables
- `DATABASE_URL`
- `SECRET_KEY`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `CORS_ALLOWED_ORIGINS`
- `LOCAL_STORAGE_DIR`
- `MAX_ATTACHMENT_SIZE_BYTES`
- `MAX_IMPORT_SIZE_BYTES`
- `VITE_API_BASE_URL`

## Troubleshooting
### Backend cannot connect to DB
- Verify `DATABASE_URL`.
- Ensure `db` container is healthy.
- Re-run migrations.

### Login fails
- Ensure seed ran successfully.
- Verify `SEED_ADMIN_EMAIL`/`SEED_ADMIN_PASSWORD` values.

### Frontend cannot reach API
- Verify `VITE_API_BASE_URL`.
- Verify backend CORS via `CORS_ALLOWED_ORIGINS`.

### Attachments fail to upload
- Verify file extension is allowed.
- Verify file size does not exceed `MAX_ATTACHMENT_SIZE_BYTES`.
- Ensure `LOCAL_STORAGE_DIR` is writable.
