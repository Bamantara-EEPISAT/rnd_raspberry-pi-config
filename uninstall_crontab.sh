#!/bin/bash
# Removes crontab entries that reference the provided login script path
set -euo pipefail

DEFAULT_SCRIPT_PATH="/home/pi/login.sh"
SCRIPT_PATH="${1:-$DEFAULT_SCRIPT_PATH}"

if ! crontab -l >/dev/null 2>&1; then
  echo "No crontab for current user. Nothing to remove."
  exit 0
fi

# Filter out lines that contain the script path
crontab -l 2>/dev/null | grep -v -F "$SCRIPT_PATH" | crontab -

echo "Removed crontab entries referencing: $SCRIPT_PATH"
