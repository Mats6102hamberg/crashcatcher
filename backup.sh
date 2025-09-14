#!/bin/bash

# CrashCatcher Backup Script
# Run this daily via cron: 0 2 * * * /path/to/backup.sh

set -e

BACKUP_DIR="/home/$(whoami)/backups"
DATE=$(date +%Y%m%d_%H%M%S)
COMPOSE_FILE="docker-compose.prod.yml"

# Create backup directory
mkdir -p $BACKUP_DIR

echo "🗄️ Starting CrashCatcher backup - $DATE"

# Backup database
echo "📦 Backing up PostgreSQL database..."
docker-compose -f $COMPOSE_FILE exec -T db pg_dump -U crashcatcher_user security_monitor | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Backup application data
echo "📁 Backing up application data..."
tar -czf $BACKUP_DIR/app_backup_$DATE.tar.gz \
    .env.prod \
    Caddyfile \
    docker-compose.prod.yml \
    --exclude=node_modules \
    --exclude=.git

# Clean old backups (keep last 7 days)
echo "🧹 Cleaning old backups..."
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "✅ Backup completed: $BACKUP_DIR"
