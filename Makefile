.PHONY: up down restart logs build clean

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

start: up

stop: down

