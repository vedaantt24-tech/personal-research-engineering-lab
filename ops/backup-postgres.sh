#!/bin/sh
set -eu
: "${POSTGRES_CONTAINER:?Set POSTGRES_CONTAINER to the database container name}"
: "${BACKUP_DIR:=./backups}"
mkdir -p "$BACKUP_DIR"
timestamp=$(date -u +%Y%m%dT%H%M%SZ)
filename="$BACKUP_DIR/personal-lab-$timestamp.sql.gz"
docker exec "$POSTGRES_CONTAINER" sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB"' | gzip > "$filename"
echo "Backup written to $filename"
