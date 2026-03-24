# Beisser Internal Operations Platform (Foundation)

A reusable internal web-application foundation for Beisser Lumber operational workflows. This base project is designed for long-term module growth (products, vendors, imports, dashboards, attachments, review workflows), not a one-off prototype.

## Stack

- **Backend:** Python 3.12, FastAPI, SQLAlchemy, Alembic, Pydantic
- **Frontend:** React, Vite, TypeScript, Material UI
- **Database:** PostgreSQL
- **Dev/Deploy:** Docker, Docker Compose
- **Auth (MVP):** JWT bearer auth with role-based user model (`admin`, `standard`)

## Project Purpose

This app provides business-friendly operational layers on top of ERP data/processes that are difficult to use directly for:

- internal product/vendor data workspace
- vendor mapping and cross-reference workflows
- import tracking and review
- attachment/note-enabled operational support
- future branch-specific internal dashboards

## Local Setup (Docker)

1. Copy environment template:
   ```bash
   cp .env.example .env
   ```
2. Start all services:
   ```bash
   docker compose up --build
   ```
3. Run migrations:
   ```bash
   docker compose exec backend alembic upgrade head
   ```
4. Seed admin/sample data:
   ```bash
   docker compose exec backend python scripts_seed.py
   ```

## Dev URLs

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api/v1
- Health endpoint: http://localhost:8000/api/v1/health

## Seed Login (Development)

- Email: `admin@beisser-internal.local`
- Password: `ChangeMe123!`

> Change this immediately in non-local environments.

## Migrations

- Create migration (inside backend container):
  ```bash
  docker compose exec backend alembic revision --autogenerate -m "message"
  ```
- Apply migration:
  ```bash
  docker compose exec backend alembic upgrade head
  ```

## Docker Notes

- `db` runs Postgres 16
- `backend` runs FastAPI + autoreload
- `frontend` runs Vite dev server

## Deployment Notes (Railway / Render)

- Both platforms support this stack well with managed PostgreSQL.
- For production:
  - build frontend static assets and serve via CDN or edge/static host
  - run backend as long-running web service
  - inject secrets and DB URL from platform env vars
  - rotate `SECRET_KEY` and seed/admin credentials

## Documentation

- Architecture: [`docs/architecture.md`](docs/architecture.md)
- Setup + troubleshooting: [`docs/setup.md`](docs/setup.md)
- Step implementation summary: [`docs/implementation-summary.md`](docs/implementation-summary.md)
