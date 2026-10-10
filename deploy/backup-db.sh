#!/usr/bin/env bash
# Dump Postgres to /opt/ai-tutor/backups and keep the last 14 days.
# Schedule daily as the deploy user (crontab -e):
#
#   15 3 * * * /opt/ai-tutor/deploy/backup-db.sh >> /opt/ai-tutor/backups/backup.log 2>&1

set -euo pipefail

cd "$(dirname "$0")/.."

set -a; . ./.env; set +a

mkdir -p backups
file="backups/db-$(date +%Y%m%d-%H%M%S).sql.gz"

docker compose -f docker-compose.prod.yml exec -T db \
  pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" | gzip > "$file"

find backups -name 'db-*.sql.gz' -mtime +14 -delete
echo "$(date -Is) wrote $file"
