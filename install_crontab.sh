#!/bin/bash
# Installs a daily cronjob to run a login script
set -euo pipefail

CRON_TIME="5 0 * * *"
DEFAULT_SCRIPT_PATH="/home/eepisat/rnd_raspberry-pi-config/login.sh"

SCRIPT_PATH="${1:-$DEFAULT_SCRIPT_PATH}"

if [ ! -f "$SCRIPT_PATH" ]; then
  echo "Warning: script not found at $SCRIPT_PATH"
fi

# Ensure crontab contains the entry (no duplicates)
CRON_CMD="$CRON_TIME $SCRIPT_PATH >> /var/log/login_cron.log 2>&1"
REBOOT_CMD1="@reboot /bin/bash /home/eepisat/rnd_raspberry-pi-config/login.sh >> /home/eepisat/startup_cron.log 2>&1"

# Read existing crontab
if crontab -l 2>/dev/null | grep -F "$SCRIPT_PATH" >/dev/null 2>&1; then
  echo "A crontab entry referencing $SCRIPT_PATH already exists. No changes made."
  exit 0
fi

(crontab -l 2>/dev/null; echo "$CRON_CMD"; echo "$REBOOT_CMD1"; echo "$REBOOT_CMD2") | crontab -
echo "Installed crontab entries:"
echo "$CRON_CMD"
echo "$REBOOT_CMD1"
echo "$REBOOT_CMD2"
