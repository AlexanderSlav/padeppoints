DB_SERVICE_NAME?=highlights-db
API_SERVICE_NAME?=highlights-api

include .env

.PHONY: build
build:  ## Build the containers
	docker compose --profile test build

.PHONY: up
up:  ## Up all the containers without test service
	docker compose up -d --force-recreate

# .PHONY: insert_admin
# insert_admin:
# 	docker exec -it $(DB_SERVICE_NAME) psql -d $(DB_NAME) -U $(DB_USERNAME) -c "INSERT INTO users (id, created_at, password_hash, is_active, role_name) VALUES ('admin', now(), '$(ADMIN_PASSWORD_HASH)', true, 'Admin');"

# .PHONY: insert_moderator
# insert_moderator:
# 	docker exec -it $(DB_SERVICE_NAME) psql -d $(DB_NAME) -U $(DB_USERNAME) -c "INSERT INTO users (id, created_at, password_hash, is_active, role_name) VALUES ('moderator', now(), '$(MODERATOR_PASSWORD_HASH)', true, 'Moderator');"

# .PHONY: insert_viewer
# insert_viewer:
# 	docker exec -it $(DB_SERVICE_NAME) psql -d $(DB_NAME) -U $(DB_USERNAME) -c "INSERT INTO users (id, created_at, password_hash, is_active, role_name) VALUES ('viewer', now(), '$(VIEWER_PASSWORD_HASH)', true, 'Viewer');"

# .PHONY: insert_default_users
# insert_default_users: insert_admin insert_moderator insert_viewer

# .PHONY: up_with_test
# up_with_test:  ## Up all the containers including test service which is used for testing
# 	docker compose --profile test up -d --force-recreate
# 	# Wait a bit for the DB to be ready
# 	sleep 5
# 	$(MAKE) insert_default_users

# .PHONY: down
# down:  ## Down the containers
# 	docker compose down

# .PHONY: connect_db
# connect_db:  ## Connect to Postgres container
# 	docker exec -it $(DB_SERVICE_NAME) psql -d ${DB_NAME} -U ${DB_USERNAME}

# .PHONY: connect_api
# connect_api:  ## Connect to API container
# 	docker exec -it $(API_SERVICE_NAME) /bin/bash

# .PHONY: drop_db_tables
# drop_db_tables:  ## Drop all tables in the database (for dev purposes only; be careful!)
# 	docker exec -it $(DB_SERVICE_NAME) psql -d ${DB_NAME} -U ${DB_USERNAME} -c "DROP TABLE IF EXISTS users; DROP TABLE IF EXISTS s3p_events; DROP TABLE IF EXISTS roles; DROP TABLE IF EXISTS streams; DROP TABLE IF EXISTS matches; DROP TABLE IF EXISTS jobs; DROP TABLE IF EXISTS alembic_version;"

# .PHONY: logs
# logs:  ## Show logs
# 	@while true; do \
# 		if docker compose ps | grep -q "Up"; then \
# 			echo "Containers are running. Attaching to logs..."; \
# 			docker compose --profile test logs -f; \
# 		else \
# 			echo "No running containers. Waiting for containers to start..."; \
# 		fi; \
# 			sleep 5; \
# 		done

# .PHONY: style
# style:  ## Format code
# 	pre-commit run --all-files

# .PHONY: migration-auto
# migration-auto:  ## Create an auto-generated migration
# 	docker exec -it $(API_SERVICE_NAME) bash -c "cd /app && alembic revision --autogenerate -m '$(name)'"

# .PHONY: help
# help:  ## Show help
# 	@grep -hE '^[A-Za-z0-9_ \-]*?:.*##.*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
