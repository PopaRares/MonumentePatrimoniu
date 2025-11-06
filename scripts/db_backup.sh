#!/bin/bash
# Backup database to SQL file

BACKUP_DIR="$(dirname "$0")/../db_backups"
mkdir -p "$BACKUP_DIR"

BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql"
docker exec patrimoniu-postgres pg_dump -U admin patrimoniu > "$BACKUP_FILE"
echo "Backup created: $BACKUP_FILE"
