.PHONY: up down restart logs build clean backup restore

up:
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

