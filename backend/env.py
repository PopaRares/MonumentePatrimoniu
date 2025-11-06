"""Environment configuration constants loaded from .env file."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root (one level up from backend/)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# PostgreSQL configuration
POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
POSTGRES_DB = os.getenv("POSTGRES_DB", "patrimoniu")

# Database URL
# For local development (outside Docker)
DATABASE_URL_LOCAL = os.getenv(
    "DATABASE_URL_LOCAL",
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:5432/{POSTGRES_DB}"
)
# For Docker/containerized environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@postgres:5432/{POSTGRES_DB}"
)

