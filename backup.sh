#!/bin/bash
# ShadowCore Backup Script to GitHub

BACKUP_ROOT="/opt/shadowcore_backup"
SOURCE_DIR="/opt/shadowcore"
LOG_FILE="$BACKUP_ROOT/backup.log"

# Log function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

cd "$BACKUP_ROOT" || exit 1

log "Starting ShadowCore backup..."

# Copy essential directories
rsync -av --delete \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='node_modules' \
    "$SOURCE_DIR/" "$BACKUP_ROOT/shadowcore/"

# Add, commit, and push to GitHub
git add -A
git commit -m "Automated backup $(date '+%Y-%m-%d %H:%M:%S')"

# Push to GitHub
if git push -u origin main; then
    log "Backup completed and pushed to GitHub successfully."
else
    log "ERROR: Failed to push backup to GitHub."
    exit 1
fi
