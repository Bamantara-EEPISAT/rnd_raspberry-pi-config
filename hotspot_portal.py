# @reboot sudo python3 /home/<username>/<this-folder>/app.py

from flask import Flask, request
import subprocess

app = Flask(__name__)

wifi_device = "wlan1"

def get_current_wifi_status():
    try:
        # Get connection status
        status_result = subprocess.run(["nmcli", "-g", "GENERAL.STATE", "device", "show", wifi_device], 
                                      capture_output=True, text=True)
        status = status_result.stdout.strip()
        
        # Get current SSID if connected
        if "connected" in status.lower():
            ssid_result = subprocess.run(["nmcli", "-g", "GENERAL.CONNECTION", "device", "show", wifi_device], 
                                        capture_output=True, text=True)
            current_ssid = ssid_result.stdout.strip()
            
            # Get IP address
            ip_result = subprocess.run(["nmcli", "-g", "IP4.ADDRESS", "device", "show", wifi_device], 
                                      capture_output=True, text=True)
            ip_address = ip_result.stdout.strip()
            
            return {
                "status": "Connected",
                "ssid": current_ssid,
                "ip": ip_address
            }
        else:
            return {"status": "Disconnected", "ssid": "N/A", "ip": "N/A"}
    except Exception as e:
        return {"status": "Error", "ssid": "N/A", "ip": "N/A", "error": str(e)}

@app.route('/')
def index():
    # Get current WiFi status
    wifi_status = get_current_wifi_status()
    
    # Get available networks
    result = subprocess.check_output(["nmcli", "--colors", "no", "-m", "multiline", "--get-value", "SSID", "dev", "wifi", "list", "ifname", wifi_device])
    ssids_list = result.decode().split('\n')
    
    # Create HTML
    dropdowndisplay = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Wifi Control</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .status-box {{ background-color: #f0f0f0; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .status-connected {{ background-color: #d4edda; }}
                .status-disconnected {{ background-color: #f8d7da; }}
                .status-error {{ background-color: #fff3cd; }}
                h1 {{ color: #333; }}
                form {{ margin-top: 20px; }}
                label {{ display: block; margin-top: 10px; }}
                input[type="submit"] {{ margin-top: 15px; padding: 8px 15px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer; }}
                input[type="submit"]:hover {{ background-color: #45a049; }}
            </style>
        </head>
        <body>
            <h1>WiFi Control</h1>
            
            <div class="status-box {'status-connected' if wifi_status['status'] == 'Connected' else 'status-disconnected' if wifi_status['status'] == 'Disconnected' else 'status-error'}">
                <h2>Current WiFi Status</h2>
                <p><strong>Status:</strong> {wifi_status['status']}</p>
                <p><strong>Network:</strong> {wifi_status['ssid']}</p>
                <p><strong>IP Address:</strong> {wifi_status['ip']}</p>
            </div>
            
            <form action="/submit" method="post">
                <label for="ssid">Choose a WiFi network:</label>
                <select name="ssid" id="ssid">
    """
    
    for ssid in ssids_list:
        only_ssid = ssid.removeprefix("SSID:")
        if len(only_ssid) > 0:
            selected = 'selected' if only_ssid == wifi_status['ssid'] else ''
            dropdowndisplay += f"""
                    <option value="{only_ssid}" {selected}>{only_ssid}</option>
            """
    
    dropdowndisplay += f"""
                </select>
                <p/>
                <label for="password">Password: <input type="password" name="password"/></label>
                <p/>
                <input type="submit" value="Connect">
            </form>
        </body>
        </html>
    """
    return dropdowndisplay

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        print(*list(request.form.keys()), sep=", ")
        ssid = request.form['ssid']
        password = request.form['password']
        connection_command = ["nmcli", "--colors", "no", "device", "wifi", "connect", ssid, "ifname", wifi_device]
        if len(password) > 0:
            connection_command.append("password")
            connection_command.append(password)
        result = subprocess.run(connection_command, capture_output=True)
        if result.stderr:
            return "Error: failed to connect to wifi network: <i>%s</i>" % result.stderr.decode()
        elif result.stdout:
            return "Success: <i>%s</i>" % result.stdout.decode()
        return "Error: failed to connect."

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)