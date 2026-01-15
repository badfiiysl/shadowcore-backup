#!/bin/bash
echo "💣 SHADOWCORE NUCLEAR CLEANUP INITIATED"
echo "======================================="

# 1. KILL ALL MONITOR/WATCHDOG PROCESSES
echo "1. Killing all monitor/watchdog processes..."
pkill -9 -f "monitor"
pkill -9 -f "watchdog"
pkill -9 -f "check.*service"
pkill -9 -f "auto.*restart"
pkill -9 -f "health.*check"

# 2. DISABLE ALL CRON JOBS
echo "2. Removing ALL cron jobs..."
crontab -r  # NUCLEAR: Remove ALL cron jobs
echo "Crontab cleared"

# 3. DISABLE ALL SYSTEMD TIMERS
echo "3. Stopping ALL timers..."
systemctl list-timers --all --no-pager | awk 'NR>1 {print $1}' | while read timer; do
    systemctl stop "$timer" 2>/dev/null
    systemctl disable "$timer" 2>/dev/null
    echo "  Stopped: $timer"
done

# 4. RENAME ALL MONITOR SCRIPTS
echo "4. Disabling ALL monitor scripts..."
find /opt /root /home -name "*monitor*" -type f \( -name "*.sh" -o -name "*.py" \) ! -path "*/node_modules/*" 2>/dev/null | while read file; do
    if [[ "$file" != *.DISABLED ]] && [[ "$file" != *.bak ]]; then
        mv "$file" "$file.NUKED" 2>/dev/null
        echo "  Disabled: $file"
    fi
done

# 5. RENAME ALL FIX/REPAIR SCRIPTS
echo "5. Disabling ALL fix/repair scripts..."
find /opt /root -name "*fix*" -type f \( -name "*.sh" -o -name "*.py" \) ! -path "*/node_modules/*" 2>/dev/null | while read file; do
    if [[ "$file" != *.NUKED ]] && [[ "$file" != *.DISABLED ]] && [[ "$file" != *.bak ]]; then
        mv "$file" "$file.NUKED" 2>/dev/null
        echo "  Disabled: $file"
    fi
done

# 6. REMOVE ALL KILL-RELATED SCRIPTS
echo "6. Removing kill-related scripts..."
for script in /root/*.sh; do
    if [ -f "$script" ]; then
        if grep -q -E "pkill.*shadow|kill.*shadow" "$script" 2>/dev/null; then
            mv "$script" "$script.NUKED"
            echo "  Nuked killer script: $script"
        fi
    fi
done

# 7. CHECK FOR RUNNING SERVICES
echo "7. Checking running services (NOT stopping them)..."
systemctl list-units --type=service --state=running | grep shadow

# 8. CREATE SAFE ENVIRONMENT
echo "8. Creating safe environment..."
cat > /root/README_RECOVERY.md << 'EOM'
# SHADOWCORE RECOVERY

## What happened:
All automatic monitors, watchdogs, and killer scripts have been disabled.

## Your services should now:
1. Run without being randomly killed
2. Stay up unless they actually crash
3. Not trigger Hetzner shutdowns

## To restart services manually:
sudo systemctl restart shadowcore-shadowbrain
sudo systemctl restart shadowcore-shadowsearch
sudo systemctl restart shadowcore-main-api
sudo systemctl restart shadowcore-auth

## To monitor safely:
watch "ss -tln | grep -E ':800[1-6]|:9090'"

## To add back SAFE monitoring later:
1. Edit /etc/crontab
2. Add: */30 * * * * root /opt/shadowcore/safe_monitor.sh
3. Keep it SIMPLE - no killing!

EOM

echo "✅ NUCLEAR CLEANUP COMPLETE"
echo "📄 Recovery guide: /root/README_RECOVERY.md"
