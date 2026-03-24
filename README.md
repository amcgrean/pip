# Beisser Internal Operations Platform (Foundation + MVP Module)

This repository now includes the first production-ready internal module: **Internal Product / Vendor Data Workspace**.

## Stack
- Backend: FastAPI, SQLAlchemy, Alembic, Pydantic
- Frontend: React + Vite + TypeScript + Material UI
- Database: PostgreSQL

## Implemented MVP Scope
- Product list with server-backed pagination, search, and filters.
- Product detail with core info, vendor mappings, attachments, and notes.
- Product create/edit APIs.
- Vendor list + create/edit APIs and UI basics.
- Vendor mapping create/update with single-primary behavior per product.
- Product notes add/list with type + timestamp.
- Product attachments upload/list/download with local file storage abstraction.
- CSV import workflow (upload, parse, trim, required column validation, upsert, row-level errors, job history).
- Dashboard summary cards and quick links.

## CSV Import Columns
Required:
- `internal_sku`
- `normalized_name`
- `vendor_code`
- `vendor_sku`

Supported optional columns:
- `product_type`, `category_major`, `category_minor`, `species_or_material`, `grade`
- `thickness`, `width`, `length`, `unit_of_measure`, `description`, `status`
- `vendor_description`, `vendor_uom`, `last_cost`

## Local file storage behavior (development)
- Attachments are stored under `local_storage_dir` (default: `./data_storage`).
- Storage implementation is abstracted behind a storage service for future cloud object storage swap.

## Deferred
- SSO, advanced authorization, ERP sync, background queues, OCR/extraction, advanced analytics, notifications, cloud object storage.

## Setup
Follow `docs/setup.md` for Docker-based setup.
