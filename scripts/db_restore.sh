#!/bin/bash
# Restore database from SQL file

if [ -z "$1" ]; then
    echo "Usage: ./db_restore.sh <backup_file.sql>"
    exit 1
fi

if [ ! -f "$1" ]; then
    echo "Error: Backup file not found: $1"
    exit 1
fi

docker exec -i patrimoniu-postgres psql -U admin patrimoniu < "$1"
echo "Database restored from $1"
