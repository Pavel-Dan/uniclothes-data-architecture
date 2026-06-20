#!/usr/bin/env bash
# Backup PostgreSQL database for UNICLOTHES POC
set -euo pipefail

BACKUP_DIR="${1:-./backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
CONTAINER="${POSTGRES_CONTAINER:-uniclothes-postgres}"
POSTGRES_USER="${POSTGRES_USER:-uniclothes}"
POSTGRES_DB="${POSTGRES_DB:-uniclothes}"

mkdir -p "$BACKUP_DIR"
BACKUP_FILE="$BACKUP_DIR/uniclothes_${TIMESTAMP}.sql.gz"

echo "Backing up $POSTGRES_DB to $BACKUP_FILE..."
docker exec "$CONTAINER" pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" | gzip > "$BACKUP_FILE"
echo "Backup complete: $BACKUP_FILE ($(du -h "$BACKUP_FILE" | cut -f1))"
