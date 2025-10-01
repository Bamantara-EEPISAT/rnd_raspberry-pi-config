#!/bin/bash
# ----------------------------------------------------------------------
# Flutter-pi Automated Setup Script for Raspberry Pi OS Lite (CLI)
# ----------------------------------------------------------------------
# This script performs the following actions:
# 1. Updates the system packages.
# 2. Installs required system dependencies (graphics, input, build tools).
# 3. Clones and installs the Flutter Engine Binaries for ARM.
# 4. Clones, compiles, and installs the flutter-pi embedder.
# 5. Sets necessary user permissions (render, input, dialout).
# 6. Runs the user's Flutter application.

set -e # Exit immediately if a command exits with a non-zero status
LOG_FILE="/tmp/flutter_pi_setup.log"
USER_NAME=$(whoami)

echo "Starting Flutter-pi setup for user: $USER_NAME" | tee "$LOG_FILE"
echo "Logging output to $LOG_FILE. Please stand by..."

# --- 1. Update and Upgrade System ---
echo -e "\n[STEP 1/5] Updating system packages..." | tee -a "$LOG_FILE"
sudo apt update -y >> "$LOG_FILE" 2>&1
sudo apt upgrade -y >> "$LOG_FILE" 2>&1

# --- 2. Install Dependencies ---
echo -e "\n[STEP 2/5] Installing required build and runtime dependencies..." | tee -a "$LOG_FILE"

# Core dependencies: cmake, graphics libs (mesa), input libs, system utilities
DEPS="cmake libgl1-mesa-dev libgles2-mesa-dev libegl1-mesa-dev libdrm-dev libgbm-dev \
      ttf-mscorefonts-installer fontconfig libsystemd-dev libinput-dev libudev-dev \
      libxkbcommon-dev git curl build-essential libserialport-dev evtest"

sudo apt install -y $DEPS >> "$LOG_FILE" 2>&1
sudo fc-cache -f -v >> "$LOG_FILE" 2>&1
echo "Dependencies installed successfully."

# --- 3. Install Flutter Engine Binaries (Needed for flutter-pi) ---
echo -e "\n[STEP 3/5] Installing Flutter Engine Binaries..." | tee -a "$LOG_FILE"
ENGINE_DIR="$HOME/flutter-engine-binaries"

# Clone the precompiled binaries repo
if [ -d "$ENGINE_DIR" ]; then
    echo "Removing existing engine binaries directory..." | tee -a "$LOG_FILE"
    sudo rm -rf "$ENGINE_DIR"
fi

git clone --depth 1 https://github.com/ardera/flutter-engine-binaries-for-arm.git "$ENGINE_DIR" >> "$LOG_FILE" 2>&1

cd "$ENGINE_DIR"
sudo ./install.sh >> "$LOG_FILE" 2>&1
cd ~
echo "Flutter Engine Binaries installed."

# --- 4. Install flutter-pi Embedder ---
echo -e "\n[STEP 4/5] Cloning and installing flutter-pi embedder..." | tee -a "$LOG_FILE"
FLUTTER_PI_DIR="$HOME/flutter-pi"

if [ -d "$FLUTTER_PI_DIR" ]; then
    echo "Removing existing flutter-pi directory..." | tee -a "$LOG_FILE"
    sudo rm -rf "$FLUTTER_PI_DIR"
fi

git clone https://github.com/ardera/flutter-pi.git "$FLUTTER_PI_DIR" >> "$LOG_FILE" 2>&1
cd "$FLUTTER_PI_DIR"
mkdir build && cd build
cmake .. >> "$LOG_FILE" 2>&1
make -j$(nproc) >> "$LOG_FILE" 2>&1
sudo make install >> "$LOG_FILE" 2>&1
cd ~
echo "Flutter-pi compiled and installed to /usr/local/bin."

# --- 5. Set Permissions ---
echo -e "\n[STEP 5/5] Setting user permissions (render, input, dialout)..." | tee -a "$LOG_FILE"
# 'render' for GPU access, 'input' for mouse/keyboard, 'dialout' for serial port
sudo usermod -a -G render "$USER_NAME"
sudo usermod -a -G input "$USER_NAME"
sudo usermod -a -G dialout "$USER_NAME"
echo "Permissions set. NOTE: You MUST reboot for these permissions to take full effect."

# --- 6. Final Execution Prompt ---

echo -e "\n-----------------------------------------------------" | tee -a "$LOG_FILE"
echo "Setup Complete!" | tee -a "$LOG_FILE"
echo "-----------------------------------------------------" | tee -a "$LOG_FILE"

# Ask user for the app path
read -rp "Enter the absolute path to your Flutter app bundle (e.g., /home/pi/my_gcs_app): " APP_PATH

if [ -z "$APP_PATH" ]; then
    echo "No path provided. Exiting script." | tee -a "$LOG_FILE"
else
    echo "Attempting to run the app in release mode:" | tee -a "$LOG_FILE"
    # Execute the app using flutter-pi in release mode
    # The 'exec' command replaces the current shell with the flutter-pi process
    echo "Command: flutter-pi --release $APP_PATH" | tee -a "$LOG_FILE"
    
    # Check if the user is running the script via sudo, if so, drop privileges for execution
    if [ "$USER_NAME" != "root" ] && [ -x /usr/local/bin/flutter-pi ]; then
        /usr/local/bin/flutter-pi --release "$APP_PATH"
    elif [ -x /usr/bin/flutter-pi ]; then
         /usr/bin/flutter-pi --release "$APP_PATH"
    else
        echo "flutter-pi executable not found in /usr/local/bin or /usr/bin. Cannot run the app." | tee -a "$LOG_FILE"
    fi
fi

echo -e "\nScript finished. If the app failed to run, please check $LOG_FILE for details."
echo "If input (mouse/keyboard) is freezing, perform a 'sudo reboot' now."
# The reboot is essential for group permissions to take effect.
