DB_SERVICE_NAME?=padel_db
API_SERVICE_NAME?=padel_web
FRONTEND_SERVICE_NAME?=padel_frontend

include .env

.PHONY: build
build:  ## Build all containers
	docker compose build

.PHONY: build-frontend
build-frontend:  ## Build only frontend container
	docker compose build frontend

.PHONY: build-backend
build-backend:  ## Build only backend container
	docker compose build web

.PHONY: up
up:  ## Start all services (database, backend, frontend)
	docker compose up -d --force-recreate

.PHONY: up-backend
up-backend:  ## Start only backend services (database + API)
	docker compose up -d db web --force-recreate

.PHONY: dev
dev:  ## Start backend in development mode with hot reloading
	docker compose up db web --force-recreate

.PHONY: dev-frontend
dev-frontend:  ## Start frontend in development mode with hot reloading
	docker compose up frontend --force-recreate

.PHONY: dev-full
dev-full:  ## Start full stack in development mode (backend + frontend)
	docker compose up db web frontend --force-recreate

.PHONY: up-frontend
up-frontend:  ## Start only frontend service
	docker compose up -d frontend --force-recreate

.PHONY: down
down:  ## Stop all containers
	docker compose down

.PHONY: logs
logs:  ## Show logs for all services
	docker compose logs -f

.PHONY: logs-frontend
logs-frontend:  ## Show logs for frontend service
	docker compose logs -f frontend

.PHONY: logs-backend
logs-backend:  ## Show logs for backend service
	docker compose logs -f web

.PHONY: logs-db
logs-db:  ## Show logs for database service
	docker compose logs -f db


.PHONY: connect-db
connect-db:  ## Connect to Postgres container
	docker exec -it $(DB_SERVICE_NAME) psql -d ${DB_NAME} -U ${DB_USERNAME}

.PHONY: connect-backend
connect-backend:  ## Connect to backend container
	docker exec -it $(API_SERVICE_NAME) /bin/bash

.PHONY: connect-frontend
connect-frontend:  ## Connect to frontend container
	docker exec -it $(FRONTEND_SERVICE_NAME) /bin/sh

.PHONY: migration
migration:  ## Make a new migration
	@if [ -z "$(m)" ]; then \
		echo "Error: Migration message not provided. Usage: make make-migration m='your migration message'"; \
		exit 1; \
	fi
	docker exec -it $(API_SERVICE_NAME) alembic revision --autogenerate -m "$(m)"

.PHONY: drop_db_tables
drop_db_tables:  ## Drop all tables and types in the database (for dev purposes only; be careful!)
	docker exec -it $(DB_SERVICE_NAME) psql -d ${DB_NAME} -U ${DB_USERNAME} -c "DROP TABLE IF EXISTS users, tournaments, rounds, tournament_player, alembic_version CASCADE;"
	docker exec -it $(DB_SERVICE_NAME) psql -d ${DB_NAME} -U ${DB_USERNAME} -c "DROP TYPE IF EXISTS tournamentsystem CASCADE;"

.PHONY: reset-db
reset-db:  ## Reset database completely and run migrations (DEV ONLY - LOSES DATA!)
	$(MAKE) drop_db_tables
	docker exec -it $(API_SERVICE_NAME) alembic upgrade head

.PHONY: fix-migration-sync
fix-migration-sync:  ## Fix migration sync issues (production-safe)
	@echo "Checking migration status..."
	docker exec -it $(API_SERVICE_NAME) alembic current
	@echo "Running migrations..."
	docker exec -it $(API_SERVICE_NAME) alembic upgrade head

.PHONY: migration-status
migration-status:  ## Show current migration status
	docker exec -it $(API_SERVICE_NAME) alembic current
	docker exec -it $(API_SERVICE_NAME) alembic history

.PHONY: create-superuser
create-superuser:  ## Create the first superuser (run interactively)
	python scripts/create_first_superuser.py

.PHONY: create-superuser-docker
create-superuser-docker:  ## Create the first superuser in Docker container
	docker exec -it $(API_SERVICE_NAME) python scripts/create_first_superuser.py


.PHONY: help
help:  ## Show help
	@grep -hE '^[A-Za-z0-9_ \-]*?:.*##.*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
