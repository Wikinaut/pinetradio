#!/usr/bin/env python3

# Get signal strength and basic network adapter parameters

# Signal strenght by foot:
# /bin/cat /proc/net/wireless | awk 'NR==3 {print $4}' | sed 's/\.//'

import subprocess
import socket
from datetime import datetime

def now():
        currentDateAndTime = datetime.now()
        return currentDateAndTime.strftime("%Y%m%d-%H%M%S")

def get_rssi(interface):    # ie, 'wlan0'
    proc = subprocess.Popen(
	["/usr/sbin/iwlist", interface, "scan"],
	stdout=subprocess.PIPE,
	universal_newlines=True)
    out, err = proc.communicate()
    out = out.split("\n")

    for i, val in enumerate(out):

        if 'Signal' in val:
            signal_line = val.split()
            if 'Signal' in signal_line:
                rssi = int(signal_line[signal_line.index('Signal')+1].split('=')[1])

        if 'ESSID' in val:
            # ESSID:"MYNETWORKSSID"
            ssid_line = val.split('"')
            ssid = ssid_line[1]

    return ssid,rssi


hostname = socket.gethostname()
ipaddr = socket.gethostbyname(hostname)
network = get_rssi('wlan0')
# print("Hostname {0}\nIP {1}\nSSID {2} {3} dB".format(hostname, ipaddr, network[0], network[1]))
print(f"{now()} {network[1]} db")
