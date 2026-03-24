# Architecture Overview

## Why this architecture for Beisser Lumber

This foundation emphasizes practical maintainability, predictable patterns, and low-ops deployment.

- Python/FastAPI aligns with current internal tooling familiarity.
- SQLAlchemy + Alembic provide durable schema control for ERP-adjacent data workflows.
- React + Material UI gives fast internal UX iteration with reusable layout/navigation.
- Dockerized services support local onboarding and cloud portability (Railway/Render).

## Repository Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── core/           # config/security
│   │   ├── db/             # base/session
│   │   ├── models/         # SQLAlchemy domain models
│   │   ├── routes/         # API route modules
│   │   ├── schemas/        # Pydantic API schemas
│   │   ├── services/       # auth/service logic
│   │   └── utils/          # auth deps
│   ├── alembic/
│   │   └── versions/       # migration history
│   └── scripts_seed.py     # initial seed data
├── frontend/
│   └── src/
│       ├── api/            # shared API client
│       ├── auth/           # auth context/state
│       ├── layout/         # reusable app shell
│       ├── pages/          # module pages
│       ├── routes/         # route + guard config
│       └── theme/          # UI theme config
├── docs/
└── docker-compose.yml
```

## Backend Overview

- FastAPI app entrypoint with versioned router prefix.
- CORS for local frontend access.
- JWT auth flow (`/auth/login`, `/auth/me`) with bcrypt password hashing.
- Protected route dependency for authenticated module access.
- Core domain models for internal product/vendor workspace:
  - users, vendors, products, vendor_product_mappings,
    product_attachments, product_notes, import_jobs.
- Alembic migration framework with initial schema migration.
- Seed script for admin account + LBM-relevant sample vendor/product records.

## Frontend Overview

- React + TypeScript + Vite app shell.
- Auth context for login/session bootstrap.
- Protected routes and login experience.
- Desktop-first left-nav layout with top app bar.
- Placeholder module pages:
  - Dashboard
  - Products
  - Vendors
  - Imports
  - Settings/Admin
- Shared axios client with bearer-token request interceptor.

## Future-fit considerations

This structure supports incremental module expansion without heavy refactors:

- new domains can add model/schema/route/service layers in parallel
- auth can evolve from JWT MVP to SSO/OIDC with minimal frontend route changes
- import workflows can add async processing (Celery/RQ) when needed
- UI shell already supports role-aware menu and module-level navigation growth
