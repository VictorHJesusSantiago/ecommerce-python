#!/bin/bash
set -e

BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/ecommerce_$TIMESTAMP.sql"

mkdir -p $BACKUP_DIR

PGPASSWORD=postgres pg_dump -h localhost -U postgres ecommerce > $BACKUP_FILE

gzip $BACKUP_FILE

find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Backup created: $BACKUP_FILE.gz"
