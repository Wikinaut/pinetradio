#!/bin/bash

# Automatic reconnect WiFi/WLAN on connection loss
#
# https://blog.spaps.de/workaround-for-raspberry-pi-automatic-wifi-wlan-reconnect/
#
# init 20230218
#
# disable power management
# sudo iwconfig wlan0 power off

# https://www.elektronik-kompendium.de/sites/raspberry-pi/1912231.htm
#
# sudo nano /etc/network/interfaces:
#
#	Folgende Zeilen eintragen bzw. fehlende Zeilen ergänzen:
#
#	allow-hotplug wlan0
#	iface wlan0 inet manual
#	post-up iw wlan0 set power_save off

verbose=0
if [[ $1 = "-v" ]]; then verbose=1 ;fi

NOW=$(date +%Y%m%d-%H%M%S)

# The IP for the server you wish to ping (get default getway)
SERVER=$(/sbin/ip route | awk '/default/ { print $3 }')

if [[ $verbose = 1 ]] ; then
	echo "$NOW Server: ${SERVER}" >>/var/log/wifi_reconnect
fi

# Specify wlan interface
WLANINTERFACE=wlan0

if [[ $verbose = 1 ]]; then
	echo "$NOW Interface: ${WLANINTERFACE}" >>/var/log/wifi_reconnect
fi

# Only send two pings, sending output to /dev/null
ping -I ${WLANINTERFACE} -c2 ${SERVER} >/dev/null

# If the return code from ping ($?) is not 0 (meaning there was an error)

if [ $? != 0 ]; then

	echo "$NOW Restarted WiFi" >> /var/log/wifi_reconnect

	# Restart the wireless interface
	ip link set wlan0 down
	ip link set wlan0 up

	# /usr/sbin/iwconfig wlan0 power off
	# Restart our internet radio
	# systemctl restart inetradio

else

	if [[ $verbose = 1 ]] ; then
		echo "$NOW WiFi works. No restart" >> /var/log/wifi_reconnect
	fi

fi
