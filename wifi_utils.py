import subprocess
import platform
import time

IS_WINDOWS = platform.system() == "Windows"

def scan_wifi():
    if IS_WINDOWS:
        # Mock data for Windows testing
        time.sleep(1.5) # Simulate scan delay
        return ["HOME-WIFI", "Guest-Network", "Office-5G", "Test-AP"]
        
    try:
        output = subprocess.check_output("nmcli -t -f SSID dev wifi", shell=True).decode()
        ssids = list({s.strip() for s in output.split("\n") if s.strip()})
        return ssids
    except:
        return []

def connect_wifi(ssid, password):
    if IS_WINDOWS:
        print(f"[MOCK] Connecting to {ssid} with password {password}...")
        time.sleep(2) # Simulate connection time
        return True # Simulate success

    try:
        cmd = f"nmcli dev wifi connect '{ssid}' password '{password}'"
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except:
        return False

def check_internet():
    if IS_WINDOWS:
        print("[MOCK] Checking internet connection...")
        time.sleep(1)
        return True

    try:
        subprocess.check_output("ping -c 1 8.8.8.8", shell=True)
        return True
    except:
        return False

def get_connected_ssid():
    if IS_WINDOWS:
        # Return None to simulate "not connected" initially so we see the Scan Page
        # Or return "HOME-WIFI" to test the already-connected flow
        return None 

    try:
        result = subprocess.check_output(
            "nmcli -t -f ACTIVE,SSID dev wifi", shell=True
        ).decode().split("\n")

        for line in result:
            if line.startswith("yes:"):
                return line.split(":")[1]
        return None
    except:
        return None
