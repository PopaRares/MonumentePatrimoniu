#!/bin/bash
# Initialize database from backup if it exists and database is empty
# This script runs automatically when postgres container starts for the first time

set -e

# Use environment variables (set by docker-compose from .env)
POSTGRES_USER="${POSTGRES_USER:-admin}"
POSTGRES_DB="${POSTGRES_DB:-patrimoniu}"

# Wait for postgres to be ready
until pg_isready -U "$POSTGRES_USER"; do
  sleep 1
done

# Check if database is empty (no tables)
TABLES=$(psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | xargs || echo "0")

if [ "$TABLES" = "0" ] || [ -z "$TABLES" ]; then
    # Database is empty, look for latest backup
    LATEST_BACKUP=$(ls -t /backups/backup_*.sql 2>/dev/null | head -1)
    
    if [ -n "$LATEST_BACKUP" ]; then
        echo "Database is empty. Restoring from latest backup: $LATEST_BACKUP"
        psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" < "$LATEST_BACKUP"
        echo "Database restored successfully"
    else
        echo "No backup found. Database will be initialized empty."
    fi
else
    echo "Database already contains data. Skipping restore."
fi
