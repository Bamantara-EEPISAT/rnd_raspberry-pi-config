#!/bin/bash
# Example launcher script for the Ground Control Station Flutter app
# Copy this to the Pi user's home (e.g., /home/pi/launch_gcs.sh) and make executable

# Path to flutter-pi binary
FLUTTER_PI_BIN="/usr/local/bin/flutter-pi"

# Path to your compiled Flutter release bundle
APP_PATH="/home/pi/my_gcs_app"

exec "$FLUTTER_PI_BIN" --release "$APP_PATH"
