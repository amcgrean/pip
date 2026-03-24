# Architecture Overview

## Module boundaries
- Routes: thin transport layer in `backend/app/routes/*`.
- Services: business logic in `backend/app/services/*`.
- Models: SQLAlchemy domain entities in `backend/app/models/*`.
- Schemas: API contracts in `backend/app/schemas/domain.py`.

## Implemented module
The Product/Vendor workspace implements reusable patterns for future operational modules:
- list/search/filter/pagination APIs
- detail-oriented aggregate endpoints
- CSV import job persistence + summary reporting
- file attachment handling with storage abstraction
- note/history capture for audit-friendly records

## Attachment storage
Current implementation uses a local filesystem storage service (`LocalStorageService`), with interfaces kept small to support a future cloud provider implementation.

## CSV import design
The import service processes each row independently to avoid whole-file failures and records row-level failures in `import_jobs.error_log`.
