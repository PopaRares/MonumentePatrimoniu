# Patrimoniu

A full-stack application with MongoDB, Python backend (FastAPI), and SvelteKit frontend.

## Quick Start

Run all services with Docker Compose:

```bash
make up
```

Or manually:
```bash
docker compose up -d
```

## Services

- **MongoDB**: Running on `localhost:27017`
- **Backend**: FastAPI running on `http://localhost:8000`
- **Frontend**: SvelteKit running on `http://localhost:5173`

## Make Commands

- `make up` - Start all services
- `make down` - Stop all services
- `make restart` - Restart all services
- `make logs` - View logs from all services
- `make logs-backend` - View backend logs
- `make logs-frontend` - View frontend logs
- `make logs-mongodb` - View MongoDB logs
- `make build` - Build all Docker images
- `make rebuild` - Rebuild and start services
- `make clean` - Stop services and clean up volumes

