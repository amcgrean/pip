# Setup & Operations Guide

## First-time setup

1. Ensure Docker Desktop (or Docker Engine + Compose plugin) is installed.
2. Copy env template:
   ```bash
   cp .env.example .env
   ```
3. Build and start services:
   ```bash
   docker compose up --build
   ```
4. In another shell, run migrations:
   ```bash
   docker compose exec backend alembic upgrade head
   ```
5. Seed baseline data:
   ```bash
   docker compose exec backend python scripts_seed.py
   ```
6. Open frontend: http://localhost:5173

## Common commands

- Start stack:
  ```bash
  docker compose up --build
  ```
- Stop stack:
  ```bash
  docker compose down
  ```
- Follow logs:
  ```bash
  docker compose logs -f backend frontend db
  ```
- Run migration:
  ```bash
  docker compose exec backend alembic upgrade head
  ```
- Seed data:
  ```bash
  docker compose exec backend python scripts_seed.py
  ```

## Troubleshooting

### Backend cannot connect to DB

- Verify `DATABASE_URL` in `.env`.
- Ensure `db` container is healthy and running.
- Re-run `docker compose up` and check backend logs.

### Login fails with seed credentials

- Ensure migrations have run.
- Re-run seed script.
- Confirm `.env` seed variables match expected login values.

### Frontend cannot reach API

- Verify `VITE_API_BASE_URL` in `.env`.
- Check CORS value for `FRONTEND_ORIGIN`.
- Confirm backend is available at `http://localhost:8000`.
