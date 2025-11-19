import subprocess

def scan_wifi():
    try:
        output = subprocess.check_output("nmcli -t -f SSID dev wifi", shell=True).decode()
        ssids = list({s.strip() for s in output.split("\n") if s.strip()})
        return ssids
    except:
        return []

def connect_wifi(ssid, password):
    try:
        cmd = f"nmcli dev wifi connect '{ssid}' password '{password}'"
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except:
        return False

def check_internet():
    try:
        subprocess.check_output("ping -c 1 8.8.8.8", shell=True)
        return True
    except:
        return False

def get_connected_ssid():
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
