#!/bin/bash

# --- Configuration ---
LOGIN_URL="https://iac2.pens.ac.id:8003/index.php?zone=eepiswlan"
COOKIE_FILE="cookies.txt"
USER_AGENT="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
POST_DATA="auth_user=disamarkan&auth_pass=disamarkan&redirurl=http%3A%2F%2Fdetectportal.brave-http-only.com%2F&accept=Login"

# --- Step 1: Fetch initial session cookies (GET request) ---
echo "--- Step 1: Fetching initial session cookies ---"
# -c / --cookie-jar: Save cookies received from server
curl -v -k "$LOGIN_URL" \
     --cookie-jar "$COOKIE_FILE" \
     -H "User-Agent: $USER_AGENT"

# --- Step 2: Submit login credentials (POST request) ---
echo -e "\n--- Step 2: Submitting login credentials ---"
# -b / --cookie: Send cookies saved in Step 1
curl -v -k -X POST "$LOGIN_URL" \
     --cookie "$COOKIE_FILE" \
     -H "User-Agent: $USER_AGENT" \
     --data "$POST_DATA"

echo -e "\nScript finished. Check the output for '200 OK' and 'Redirecting...' HTML."
