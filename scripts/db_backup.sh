#!/bin/bash
# Backup database to SQL file

# Load environment variables
SCRIPT_DIR="$(dirname "$0")"
if [ -f "$SCRIPT_DIR/../.env" ]; then
    export $(grep -v '^#' "$SCRIPT_DIR/../.env" | xargs)
fi

BACKUP_DIR="$SCRIPT_DIR/../db_backups"
mkdir -p "$BACKUP_DIR"

BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql"
docker exec patrimoniu-postgres pg_dump -U "${POSTGRES_USER:-admin}" "${POSTGRES_DB:-patrimoniu}" > "$BACKUP_FILE"
echo "Backup created: $BACKUP_FILE"
