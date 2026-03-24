.PHONY: up down logs migrate seed backend-shell

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f backend frontend db

migrate:
	docker compose exec backend alembic upgrade head

seed:
	docker compose exec backend python scripts_seed.py

backend-shell:
	docker compose exec backend bash
