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

##  TODO - Conversatie Mina 6 Noiembrie
- AI GIS location generation
    * cache it on generation? generate all at once? risky and costly. think about this.
    * allow users to report this and propose new locations
- visual map aide on frontend
- map icon for locations that have been mapped
- Map of Romania selector with counties and sub-counties (think aeip https://prezenta.roaep.ro/prezidentiale18052025/presence/table/?region=total)
- filters:
    * type of localitate
    * type of monument
    * dating period
    * category:
        - type A - national importance
        - type B - local importance
        I. Monumente de arheologie
        II. Monumente de arhitectură
        III. Monumente de for public
        IV. Monumente memoriale şi funerare
        https://www.cultura.ro/lista-monumentelor-istorice/
- users can upload photos of the monument in question
    * see it in a photo gallery on the frontend
    * minimal coordinate check? what if AI coords are wrong to begin with?
- change the font
    * sans-serif



AB-I-m-B-00073.06
[JUDET]-[CATEGORIE]-[TIPOLOGIE]-[IMPORTANTA]-[NR].[NR_COMPONENTA]


