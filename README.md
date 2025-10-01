# Raspberry Pi: flutter-pi setup & auto-login helper

This repository contains two small shell scripts that help set up and run Flutter apps on a Raspberry Pi (CLI / Raspberry Pi OS Lite) and a helper script to perform a campus/captive-portal login on a schedule.

Files
- `setup_flutter_pi.sh` - Automated installer for flutter-pi and the Flutter engine binaries. Intended to be run interactively on a Raspberry Pi user account.
- `login.sh` - A tiny curl-based login script (fill in the URL, username, and password) to authenticate against a campus portal. Intended to be run from cron.
- `install_crontab.sh` - Helper to install a cron entry for `login.sh` (created here).
- `uninstall_crontab.sh` - Helper to remove the cron entry for `login.sh` (created here).

Quick summary

- Use `setup_flutter_pi.sh` to prepare a Raspberry Pi to run Flutter apps using `flutter-pi` (graphics libs, engine binaries, build of the embedder, and groups/permissions).
- Use `login.sh` to automate a web login (campus portal); add it to cron to run at scheduled times.

Prerequisites

- A Raspberry Pi running Raspberry Pi OS (Lite) or Debian-based system.
- Internet access to download packages and clone repositories.
- `sudo` access for `setup_flutter_pi.sh` (it installs system packages and writes to system locations).

Usage

1) Make scripts executable (adjust paths if you cloned the repo to a different location):

```bash
chmod +x setup_flutter_pi.sh login.sh install_crontab.sh uninstall_crontab.sh
```

2) Run the Flutter setup script (interactive):

```bash
./setup_flutter_pi.sh
```

Notes on `setup_flutter_pi.sh`
- It updates the system, installs required packages, clones prebuilt Flutter engine binaries, builds and installs `flutter-pi`, and adds the current user to the `render`, `input`, and `dialout` groups.
- The script logs to `/tmp/flutter_pi_setup.log` and exits on any error (`set -e`).
- After running, a reboot is required for group membership changes to take effect.
- When asked for your Flutter app bundle path, pass the absolute path to the directory containing the compiled Flutter release bundle.

Usage and safety notes for `login.sh`

- Fill in the `LOGIN_URL`, `USERNAME`, and `PASSWORD` variables inside `login.sh` before using.
- Test interactively first:

```bash
./login.sh
```

- Because credentials may be present in plaintext, protect this file with filesystem permissions and consider using a secrets manager or environment variables for production use.

Cron scheduling (how to run `login.sh` automatically)

The intended cron entry (from your request) runs the script at 00:05 every day:

```
# m h  dom mon dow   command
5 0 * * * /home/pi/login.sh
```

Important:
- Use an absolute path to `login.sh` (cron runs with a limited environment).
- Redirect output to a log to capture failures, e.g.:

```
5 0 * * * /home/pi/login.sh >> /var/log/login_cron.log 2>&1
```

Install / remove the cron job using the provided helpers

Two helper scripts are provided to add/remove the cron entry: `install_crontab.sh` and `uninstall_crontab.sh`.

Install (default path = /home/pi/login.sh):

```bash
# make executable (if not already)
chmod +x install_crontab.sh
# run with optional path to the login script
./install_crontab.sh /home/pi/login.sh
```

Uninstall (removes any cron line that references the provided path):

```bash
chmod +x uninstall_crontab.sh
./uninstall_crontab.sh /home/pi/login.sh
```

Both helpers are idempotent and safe to re-run. They will not duplicate entries.

Security & troubleshooting

- Store credentials carefully. If this machine is multi-user, restrict permissions: `chmod 700 login.sh` and keep it owned by the running user.
- If cron doesn't run the script, check `/var/log/syslog` (or systemd journal) and the log file created by the cron line (`/var/log/login_cron.log` in the examples).
- Cron runs with a minimal PATH. Always use absolute paths inside `login.sh` or set PATH at the top of the script.

Notes and small extras

- `install_crontab.sh` and `uninstall_crontab.sh` are simple helpers and require `crontab` to be available. They operate on the current user's crontab.
- Adjust the schedule in `install_crontab.sh` if you need a different time.

License

- This repository contains small helper scripts. Use at your own risk. No warranty.

If you'd like, I can:

- Add an example `systemd` unit to run a Flutter app at boot instead of using an interactive launcher.

Using a systemd service (run your Flutter app at boot)

If you want your Flutter app to start automatically at boot (without an interactive login), you can use a systemd service. Below are example files and commands.

1) Create a launcher script on the Pi (example: `~/launch_gcs.sh`):

```bash
#!/bin/bash
# Replace the app path with your release bundle path
/usr/local/bin/flutter-pi --release /home/pi/my_gcs_app
```

Make it executable:

```bash
chmod +x ~/launch_gcs.sh
```

2) Create a systemd unit file (example: `/etc/systemd/system/gcs.service`):

```
[Unit]
Description=Ground Control Station Flutter App
After=network.target

[Service]
ExecStart=/home/pi/launch_gcs.sh
Restart=on-failure
User=pi
# This environment variable may be needed for some setups, but often not for pure flutter-pi/DRM
# Environment=DISPLAY=:0
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Replace `pi` with your actual username and adjust paths as needed.

3) Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable gcs.service
sudo systemctl start gcs.service
```

4) Reboot to test:

```bash
sudo reboot
```

Troubleshooting and logs
- Check the service status and logs with:

```bash
sudo systemctl status gcs.service
journalctl -u gcs.service --no-pager -n 200
```

Notes
- If your app requires GPU/DRM access or specific environment variables, add them to the service unit using `Environment=` or a small wrapper script that sets them before launching `flutter-pi`.
- Make sure the user configured for the service belongs to `render` and `input` groups if the app needs hardware access.

- Improve `login.sh` to read credentials from an encrypted file or environment variables.

---
Generated on: 2025-10-01

