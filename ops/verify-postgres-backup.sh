#!/bin/sh
set -eu
: "${BACKUP_FILE:?Set BACKUP_FILE to a .sql.gz backup}"
: "${POSTGRES_CONTAINER:?Set POSTGRES_CONTAINER to the database container name}"

# Non-destructive validation: inspect the gzip stream and first SQL statements.
gzip -t "$BACKUP_FILE"
mkdir -p "${TMP_DIR:=/tmp/personal-lab-backup-check}"
gzip -cd "$BACKUP_FILE" | head -n 20 > "$TMP_DIR/preview.sql" || true
printf 'Backup gzip integrity: OK\nPreview written to %s\n' "$TMP_DIR/preview.sql"
