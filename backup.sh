#!/bin/bash
# Complete /opt Backup Script to GitHub

BACKUP_ROOT="/opt/shadowcore_backup"
SOURCE_DIR="/opt"  # Changed from /opt/shadowcore to /opt
LOG_FILE="$BACKUP_ROOT/backup.log"

# Log function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

cd "$BACKUP_ROOT" || exit 1

log "Starting complete /opt backup..."

# Remove old backup copy
rm -rf "$BACKUP_ROOT/opt_backup"

# Copy entire /opt directory with exclusions
rsync -av --delete \
    --exclude='shadowcore_backup' \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='*.log' \
    --exclude='*.pid' \
    --exclude='*.lock' \
    --exclude='/opt/containerd' \
    --exclude='/opt/shadowcore/feeds/' \
    "$SOURCE_DIR/" "$BACKUP_ROOT/opt_backup/"

# Check if there are changes
if git diff --quiet && git diff --staged --quiet; then
    log "No changes detected. Skipping commit."
    exit 0
fi

# Add, commit, and push to GitHub
git add -A
git commit -m "Complete /opt backup $(date '+%Y-%m-%d %H:%M:%S')"

# Push to GitHub
if git push origin main; then
    log "Backup completed and pushed to GitHub successfully."
else
    log "ERROR: Failed to push backup to GitHub."
    exit 1
fi
