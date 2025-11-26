.PHONY: up down restart logs build clean backup restore

up:
	@if [ -f .env ]; then export $$(grep -v '^#' .env | xargs); fi; \
	docker compose up -d postgres; \
	echo "Waiting for postgres to be ready..."; \
	sleep 3; \
	if [ -n "$$(ls -t db_backups/backup_*.sql 2>/dev/null | head -1)" ]; then \
		echo "Restoring from latest backup..."; \
		LATEST_BACKUP=$$(ls -t db_backups/backup_*.sql | head -1); \
		docker compose exec -T postgres psql -U $${POSTGRES_USER:-admin} -d postgres -c "DROP DATABASE IF EXISTS $${POSTGRES_DB:-patrimoniu};"; \
		docker compose exec -T postgres psql -U $${POSTGRES_USER:-admin} -d postgres -c "CREATE DATABASE $${POSTGRES_DB:-patrimoniu};"; \
		docker compose exec -T postgres psql -U $${POSTGRES_USER:-admin} -d $${POSTGRES_DB:-patrimoniu} < $$LATEST_BACKUP; \
		echo "Database restored from $$LATEST_BACKUP"; \
	else \
		echo "No backup found. Starting with existing database."; \
	fi; \
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

logs-backend:
	docker compose logs -f backend

logs-frontend:
	docker compose logs -f frontend

logs-postgres:
	docker compose logs -f postgres

build:
	docker compose build

rebuild:
	docker compose up -d --build

clean:
	docker compose down -v
	docker system prune -f

backup:
	./scripts/db_backup.sh

restore:
	@if [ -z "$(FILE)" ]; then \
		echo "Usage: make restore FILE=db_backups/backup_YYYYMMDD_HHMMSS.sql"; \
		exit 1; \
	fi
	./scripts/db_restore.sh $(FILE)

start: up

stop: down

