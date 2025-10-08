# @reboot sudo python3 /home/<username>/<this-folder>/app.py

from flask import Flask, request, make_response
import subprocess
import json

app = Flask(__name__)

# Global variable to store the selected WiFi device
selected_wifi_device = None

def get_all_wifi_devices():
    """Get all available WiFi devices with their status"""
    try:
        # Get all network devices
        result = subprocess.run(["nmcli", "-t", "-f", "DEVICE,TYPE,STATE", "device", "status"], 
                               capture_output=True, text=True)
        devices = result.stdout.strip().split('\n')
        
        wifi_devices = []
        for device in devices:
            if not device.strip():
                continue
                
            dev_info = device.split(':')
            if len(dev_info) >= 3 and dev_info[1].lower() == 'wifi':
                device_name = dev_info[0]
                device_state = dev_info[2]
                
                # Check if device is in hotspot mode
                try:
                    mode_result = subprocess.run(["nmcli", "-g", "WIFI.MODE", "device", "show", device_name], 
                                               capture_output=True, text=True)
                    mode = mode_result.stdout.strip().lower()
                except:
                    mode = "unknown"
                
                # Get connection name if connected
                try:
                    conn_result = subprocess.run(["nmcli", "-g", "GENERAL.CONNECTION", "device", "show", device_name], 
                                               capture_output=True, text=True)
                    connection = conn_result.stdout.strip()
                except:
                    connection = ""
                
                wifi_devices.append({
                    "name": device_name,
                    "state": device_state,
                    "mode": mode,
                    "connection": connection
                })
        
        return wifi_devices
    except Exception as e:
        print(f"Error getting WiFi devices: {e}")
        return []

def get_wifi_device():
    """Get the currently selected WiFi device or auto-select the first available"""
    global selected_wifi_device
    
    # If we already have a selected device, verify it still exists
    if selected_wifi_device:
        devices = get_all_wifi_devices()
        for dev in devices:
            if dev["name"] == selected_wifi_device and dev["mode"] != "ap":
                return selected_wifi_device
        # Selected device no longer available or is now in hotspot mode
        selected_wifi_device = None
    
    # Auto-select the first available WiFi device not in hotspot mode
    devices = get_all_wifi_devices()
    for dev in devices:
        if dev["mode"] != "ap":
            selected_wifi_device = dev["name"]
            return selected_wifi_device
    
    return None

wifi_device = get_wifi_device()

def get_current_wifi_status():
    """Get current WiFi connection status"""
    global wifi_device
    
    if not wifi_device:
        return {"status": "No WiFi Device", "ssid": "N/A", "ip": "N/A"}
        
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

def get_available_networks():
    """Get list of available WiFi networks"""
    global wifi_device
    
    if not wifi_device:
        return []
        
    try:
        result = subprocess.check_output(["nmcli", "--colors", "no", "-m", "multiline", "--get-value", "SSID", 
                                        "dev", "wifi", "list", "ifname", wifi_device])
        ssids_list = result.decode().split('\n')
        return [ssid.removeprefix("SSID:") for ssid in ssids_list if len(ssid.removeprefix("SSID:")) > 0]
    except subprocess.CalledProcessError as e:
        print(f"Error getting WiFi networks: {e}")
        return []

def get_hotspot_status():
    """Check if any WiFi device is currently in hotspot mode"""
    devices = get_all_wifi_devices()
    return [dev for dev in devices if dev["mode"] == "ap"]

@app.route('/')
def index():
    global wifi_device
    
    # Get current WiFi status
    wifi_status = get_current_wifi_status()
    
    # Get available networks
    ssids_list = get_available_networks()
    
    # Get all WiFi devices for selection
    all_devices = get_all_wifi_devices()
    
    # Get hotspot status
    hotspot_devices = get_hotspot_status()
    
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
                .status-no-device {{ background-color: #f8d7da; }}
                .status-hotspot {{ background-color: #cce5ff; }}
                .status-selection {{ background-color: #e2e3e5; }}
                h1 {{ color: #333; }}
                form {{ margin-top: 20px; }}
                label {{ display: block; margin-top: 10px; }}
                input[type="submit"] {{ margin-top: 15px; padding: 8px 15px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer; }}
                input[type="submit"]:hover {{ background-color: #45a049; }}
                .error-message {{ color: #721c24; font-weight: bold; }}
                .info-message {{ color: #004085; font-weight: bold; }}
                .device-info {{ margin-bottom: 5px; }}
                .device-status {{ font-size: 0.9em; color: #666; }}
            </style>
        </head>
        <body>
            <h1>WiFi Control</h1>
    """
    
    # Add interface selection form
    dropdowndisplay += f"""
        <div class="status-box status-selection">
            <h2>WiFi Interface Selection</h2>
            <form action="/select_interface" method="post">
                <label for="wifi_interface">Select WiFi Interface:</label>
                <select name="wifi_interface" id="wifi_interface">
    """
    
    # Add available devices to dropdown
    for dev in all_devices:
        if dev["mode"] != "ap":  # Skip hotspot devices
            selected = 'selected' if dev["name"] == wifi_device else ''
            status_text = f" ({dev['state']}"
            if dev["connection"]:
                status_text += f" - {dev['connection']}"
            status_text += ")"
            
            dropdowndisplay += f"""
                    <option value="{dev['name']}" {selected}>{dev['name']}{status_text}</option>
            """
    
    dropdowndisplay += f"""
                </select>
                <input type="submit" value="Select Interface">
            </form>
        </div>
    """
    
    # Add hotspot status if any
    if hotspot_devices:
        dropdowndisplay += f"""
            <div class="status-box status-hotspot">
                <h2>Active Hotspot(s)</h2>
        """
        for hotspot in hotspot_devices:
            dropdowndisplay += f"""
                <div class="device-info"><strong>Device:</strong> {hotspot['name']}</div>
                <div class="device-status"><strong>Hotspot Name:</strong> {hotspot['connection']}</div>
            """
        dropdowndisplay += """
            </div>
        """
    
    # Add WiFi status box
    if wifi_status['status'] == "No WiFi Device":
        dropdowndisplay += f"""
            <div class="status-box status-no-device">
                <h2>WiFi Status</h2>
                <p class="error-message">No available WiFi device found. Please check your hardware.</p>
        """
        if hotspot_devices:
            dropdowndisplay += """
                <p class="info-message">Note: All WiFi devices are currently in hotspot mode.</p>
            """
        dropdowndisplay += """
            </div>
        """
    else:
        status_class = "status-connected" if wifi_status['status'] == 'Connected' else "status-disconnected" if wifi_status['status'] == 'Disconnected' else "status-error"
        dropdowndisplay += f"""
            <div class="status-box {status_class}">
                <h2>Current WiFi Status</h2>
                <div class="device-info"><strong>Device:</strong> {wifi_device}</div>
                <div class="device-info"><strong>Status:</strong> {wifi_status['status']}</div>
                <div class="device-info"><strong>Network:</strong> {wifi_status['ssid']}</div>
                <div class="device-info"><strong>IP Address:</strong> {wifi_status['ip']}</div>
            </div>
        """
    
    # Add network selection form if WiFi device is available
    if wifi_device:
        dropdowndisplay += f"""
            <form action="/submit" method="post">
                <label for="ssid">Choose a WiFi network:</label>
                <select name="ssid" id="ssid">
        """
        
        for ssid in ssids_list:
            selected = 'selected' if ssid == wifi_status['ssid'] else ''
            dropdowndisplay += f"""
                    <option value="{ssid}" {selected}>{ssid}</option>
            """
        
        dropdowndisplay += f"""
                </select>
                <p/>
                <label for="password">Password: <input type="password" name="password"/></label>
                <p/>
                <input type="submit" value="Connect">
            </form>
        """
    
    dropdowndisplay += """
        </body>
        </html>
    """
    return dropdowndisplay

@app.route('/select_interface', methods=['POST'])
def select_interface():
    global selected_wifi_device, wifi_device
    
    if request.method == 'POST':
        interface = request.form['wifi_interface']
        
        # Verify the interface exists and is not in hotspot mode
        devices = get_all_wifi_devices()
        for dev in devices:
            if dev["name"] == interface and dev["mode"] != "ap":
                selected_wifi_device = interface
                wifi_device = interface
                break
        
        # Redirect back to the main page
        response = make_response('', 302)
        response.headers['Location'] = '/'
        return response

@app.route('/submit', methods=['POST'])
def submit():
    global wifi_device
    
    if not wifi_device:
        return "Error: No WiFi device available", 500
        
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