#!/bin/bash

# --- Configuration ---
LOGIN_URL="YOUR_REQUEST_URL_FROM_STEP_1"
USERNAME="username@prodi.student.pens.ac.id"
PASSWORD="your_password"

# --- Send the POST request to log in ---
# The -d option sends the form data (username=value&password=value)
# The -s option makes the output silent
# The -k option is often needed for campus portals with self-signed SSL certificates
curl -s -k -X POST "$LOGIN_URL" -d "username=$USERNAME&password=$PASSWORD&submit=Login"

# Optional: Print a confirmation message to the log
echo "Login script executed at $(date)"